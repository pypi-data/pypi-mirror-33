#!/usr/bin/env python
# crate_anon/anonymise/models.py

"""
===============================================================================

    Copyright (C) 2015-2018 Rudolf Cardinal (rudolf@pobox.com).

    This file is part of CRATE.

    CRATE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CRATE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CRATE. If not, see <http://www.gnu.org/licenses/>.

===============================================================================

To create a SQLAlchemy Table programmatically:
    http://docs.sqlalchemy.org/en/latest/core/schema.html
    http://stackoverflow.com/questions/5424942/sqlalchemy-model-definition-at-execution  # noqa
    http://stackoverflow.com/questions/2580497/database-on-the-fly-with-scripting-languages/2580543#2580543  # noqa

To create a SQLAlchemy ORM programmatically:
    http://stackoverflow.com/questions/2574105/sqlalchemy-dynamic-mapping/2575016#2575016  # noqa
"""

import logging
import random
from typing import TYPE_CHECKING, Union

from cardinal_pythonlib.sqlalchemy.orm_query import exists_orm
from sqlalchemy import (
    Column,
    MetaData,
    Text,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from crate_anon.anonymise.config_singleton import config
from crate_anon.anonymise.constants import (
    MAX_TRID,
    TABLE_KWARGS,
    TridType,
)

if TYPE_CHECKING:
    from crate_anon.anonymise.scrub import PersonalizedScrubber

log = logging.getLogger(__name__)
admin_meta = MetaData()
AdminBase = declarative_base(metadata=admin_meta)


class PatientInfoConstants(object):
    SECRET_MAP_TABLENAME = 'secret_map'
    PID_FIELDNAME = "pid"
    MPID_FIELDNAME = "mpid"
    RID_FIELDNAME = "rid"
    MRID_FIELDNAME = "mrid"
    TRID_FIELDNAME = "trid"


class PatientInfo(AdminBase):
    """
    Design decision in this class:

    - It gets too complicated if you try to make the fieldnames arbitrary and
      determined by the config.

    - So we always use 'pid', 'rid', etc.

        - Older config settings that this decision removes:

          .. code-block:: none

            mapping_patient_id_fieldname
            mapping_master_id_fieldname

        - Note that these are still actively used, as they can be used to
          set the names in the OUTPUT database (not the mapping database):

          .. code-block:: none

            research_id_fieldname
            trid_fieldname
            master_research_id_fieldname
            source_hash_fieldname

    - The config is allowed to set three column types:

        - the source PID type (e.g. INT, BIGINT, VARCHAR)
        - the source MPID type (e.g. BIGINT)
        - the encrypted (RID, MRID) type (which is set by the encryption
          algorithm; e.g. VARCHAR(128) for SHA-512.
    """
    __tablename__ = PatientInfoConstants.SECRET_MAP_TABLENAME
    __table_args__ = TABLE_KWARGS

    pid = Column(
        PatientInfoConstants.PID_FIELDNAME, config.pidtype,
        primary_key=True, autoincrement=False,
        doc="Patient ID (PID) (PK)")
    rid = Column(
        PatientInfoConstants.RID_FIELDNAME, config.SqlTypeEncryptedPid,
        nullable=False, unique=True,
        doc="Research ID (RID)")
    trid = Column(
        PatientInfoConstants.TRID_FIELDNAME, TridType,
        unique=True,
        doc="Transient integer research ID (TRID)")
    mpid = Column(
        PatientInfoConstants.MPID_FIELDNAME, config.mpidtype,
        doc="Master patient ID (MPID)")
    mrid = Column(
        PatientInfoConstants.MRID_FIELDNAME, config.SqlTypeEncryptedPid,
        doc="Master research ID (MRID)")
    scrubber_hash = Column(
        'scrubber_hash', config.SqlTypeEncryptedPid,
        doc="Scrubber hash (for change detection)")
    patient_scrubber_text = Column(
        "_raw_scrubber_patient", Text,
        doc="Raw patient scrubber (for debugging only)")
    tp_scrubber_text = Column(
        "_raw_scrubber_tp", Text,
        doc="Raw third-party scrubber (for debugging only)")

    def ensure_rid(self) -> None:
        assert self.pid is not None
        if self.rid is not None:
            return
        self.rid = config.encrypt_primary_pid(self.pid)

    def ensure_trid(self, session: Session) -> None:
        assert self.pid is not None
        if self.trid is not None:
            return
        # noinspection PyTypeChecker
        self.trid = TridRecord.get_trid(session, self.pid)

    def set_mpid(self, mpid: Union[int, str]) -> None:
        self.mpid = mpid
        self.mrid = config.encrypt_master_pid(self.mpid)

    def set_scrubber_info(self, scrubber: "PersonalizedScrubber") -> None:
        self.scrubber_hash = scrubber.get_hash()
        if config.save_scrubbers:
            self.patient_scrubber_text = scrubber.get_patient_regex_string()
            self.tp_scrubber_text = scrubber.get_tp_regex_string()
        else:
            self.patient_scrubber_text = None
            self.tp_scrubber_text = None


class TridRecord(AdminBase):
    __tablename__ = 'secret_trid_cache'
    __table_args__ = TABLE_KWARGS

    pid = Column(
        "pid", config.pidtype,
        primary_key=True, autoincrement=False,
        doc="Patient ID (PID) (PK)")
    trid = Column(
        "trid", TridType,
        nullable=False, unique=True,
        doc="Transient integer research ID (TRID)")

    @classmethod
    def get_trid(cls, session: Session, pid: Union[int, str]) -> int:
        try:
            obj = session.query(cls).filter(cls.pid == pid).one()
            return obj.trid
        except NoResultFound:
            return cls.new_trid(session, pid)

    @classmethod
    def new_trid(cls, session: Session, pid: Union[int, str]) -> int:
        """
        We check for existence by inserting and asking the database if it's
        happy, not by asking the database if it exists (since other processes
        may be doing the same thing at the same time).
        """
        while True:
            session.begin_nested()
            candidate = random.randint(1, MAX_TRID)
            log.debug("Trying candidate TRID: {}".format(candidate))
            # noinspection PyArgumentList
            obj = cls(pid=pid, trid=candidate)
            try:
                session.add(obj)
                session.commit()  # may raise IntegrityError
                return candidate
            except IntegrityError:
                session.rollback()


class OptOutPid(AdminBase):
    __tablename__ = 'opt_out_pid'
    __table_args__ = TABLE_KWARGS

    pid = Column(
        'pid', config.pidtype,
        primary_key=True,
        doc="Patient ID")

    @classmethod
    def opting_out(cls, session: Session, pid: Union[int, str]) -> bool:
        return exists_orm(session, cls, cls.pid == pid)

    @classmethod
    def add(cls, session: Session, pid: Union[int, str]) -> None:
        log.debug("Adding opt-out for PID {}".format(pid))
        # noinspection PyArgumentList
        newthing = cls(pid=pid)
        session.merge(newthing)
        # http://stackoverflow.com/questions/12297156/fastest-way-to-insert-object-if-it-doesnt-exist-with-sqlalchemy  # noqa


class OptOutMpid(AdminBase):
    __tablename__ = 'opt_out_mpid'
    __table_args__ = TABLE_KWARGS

    mpid = Column(
        'mpid', config.mpidtype,
        primary_key=True,
        doc="Patient ID")

    @classmethod
    def opting_out(cls, session: Session, mpid: Union[int, str]) -> bool:
        return exists_orm(session, cls, cls.mpid == mpid)

    @classmethod
    def add(cls, session: Session, mpid: Union[int, str]) -> None:
        log.debug("Adding opt-out for MPID {}".format(mpid))
        # noinspection PyArgumentList
        newthing = cls(mpid=mpid)
        session.merge(newthing)

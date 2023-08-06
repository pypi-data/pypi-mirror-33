# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Batch-related commands
"""

from __future__ import unicode_literals, absolute_import

import logging

from rattail.commands.core import Subcommand
from rattail.progress import SocketProgress
from rattail.time import make_utc


log = logging.getLogger(__name__)


class BatchAction(Subcommand):
    """
    Base class for commands which invoke a handler to act on a batch.
    """

    def add_parser_args(self, parser):
        parser.add_argument('batch_type',
                            help="Type key of batch to be populated, e.g. 'vendor_catalog'.")
        parser.add_argument('batch_uuid',
                            help="UUID of the batch to be populated.")
        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging etc. to "
                            "occur, but rollback (abort) the transaction at the end.")

    def run(self, args):
        from rattail.batch import get_batch_handler

        handler = get_batch_handler(self.config, args.batch_type)
        if not handler:
            raise RuntimeError("Could not locate handler for batch type: {}".format(args.batch_type))

        session = self.make_session()
        user = self.get_runas_user(session)

        batch = session.query(handler.batch_model_class).get(args.batch_uuid)
        if not batch:
            raise RuntimeError("Batch of type '{}' not found: {}".format(args.batch_type, args.batch_uuid))

        success = self.action(handler, batch, user)

        if args.dry_run:
            session.rollback()
            log.info("dry run, so transaction was rolled back")
        elif success:
            session.commit()
            log.info("transaction was committed")
        else:
            session.rollback()
            log.warning("action failed, so transaction was rolled back")
        session.close()


class PopulateBatch(BatchAction):
    """
    Populate initial data for a batch
    """
    name = 'populate-batch'
    description = __doc__.strip()

    def action(self, handler, batch, user):
        return handler.do_populate(batch, user, progress=self.progress)


class RefreshBatch(BatchAction):
    """
    Refresh data for a batch
    """
    name = 'refresh-batch'
    description = __doc__.strip()

    def action(self, handler, batch, user):
        return handler.do_refresh(batch, user, progress=self.progress)


class ExecuteBatch(BatchAction):
    """
    Execute a batch
    """
    name = 'execute-batch'
    description = __doc__.strip()

    def action(self, handler, batch, user):
        return handler.do_execute(batch, user, progress=self.progress)

# -*- coding: utf-8 -*-
# Licensed to Anthony Shaw (anthonyshaw@apache.org) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import arrow
from pluralsight.models.invite import Invite


class InvitesClient(object):
    """
    Invites API
    """
    def __init__(self, client):
        self.client = client

    def get_all_invites(self):
        """
        Get all invites

        :return: A list of :class:`Invite`
        :rtype: ``list`` of :class:`Invite`
        """
        return self.get_invites()

    def get_invites(self, email=None, note=None, team_id=None):
        """
        Get invitations matching certain filters

        :param email: The users' email address
        :type  email: ``str``

        :param team_id: The team identifier
        :type  team_id: ``str``

        :param note: Additional notes on the user
        :type  note: ``str``

        :return: A list of :class:`Invite`
        :rtype: ``list`` of :class:`Invite`
        """
        params = {}
        if email is not None:
            params['email'] = email
        if note is not None:
            params['note'] = note
        if team_id is not None:
            params['teamId'] = team_id
        invites = self.client.get('invites', params=params)
        return [self._to_invite(i) for i in invites['data']]

    def get_invite(self, id):
        """
        Fetch an invitation by ID

        :param id: The identifier
        :type  id: ``str``

        :return: An instance :class:`Invite`
        :rtype: :class:`Invite`
        """
        invite = self.client.get('invites/{0}'.format(id))
        return self._to_invite(invite['data'])

    def invite_user(self, email, team_id=None, note=None):
        """
        Create a new invitation

        :param email: The users' email address
        :type  email: ``str``

        :param team_id: The team identifier
        :type  team_id: ``str``

        :param note: Additional notes on the user
        :type  note: ``str``

        :return: An instance :class:`Invite`
        :rtype: :class:`Invite`
        """
        data = {
            'data': {
                'email': email,
                'teamId': team_id,
                'note': note
            }
        }
        invite = self.client.post('invites', data=data)
        return self._to_invite(invite['data'])

    def update_invite(self, id, note):
        """
        Update an invitation

        :param id: The identifier
        :type  id: ``str``

        :param note: Additional notes on the user
        :type  note: ``str``
        """
        data = {
            'data': {
                'note': note
            }
        }
        self.client.put('invites/{0}'.format(id), data=data)

    def cancel_invite(self, id):
        """
        Cancel an invitation

        :param id: The identifier
        :type  id: ``str``

        :rtype: None
        """
        self.client.delete('invites/{0}'.format(id))

    def _to_invite(self, data):
        return Invite(
            id=data['id'],
            email=data['email'],
            team_id=data['teamId'],
            note=data['note'],
            send_date=arrow.get(data['sendDate']),
            expires_on=arrow.get(data['expiresOn'])
        )

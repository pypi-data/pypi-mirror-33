# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.

from typing import List
from EPCPyYes.core.v1_2 import events
from quartet_output.models import EPCISOutputCriteria

SourceList = List[events.Source]
DestinationList = List[events.Destination]


class EventEvaluation:

    def evaluate_event(self, event: events.EPCISBusinessEvent,
                       epc_output_criteria: EPCISOutputCriteria
                       ):
        '''
        Returns a true or false if the event meets the output criteria.
        :param event: An EPCPyYes event to evaluate.
        :param epc_output_criteria: The criteria to evaluate the event against.
        :return: boolean - True or false.
        '''
        # check the event type
        event_type = self.check_event_type(
            event,
            epc_output_criteria.event_type
        )
        action = self.check_action(
            event, epc_output_criteria.action
        )
        biz_location = self.check_biz_location(
            event,
            epc_output_criteria.biz_location
        )
        disposition = self._check_string(
            event.disposition,
            epc_output_criteria.disposition
        )
        biz_step = self._check_string(
            event.biz_step,
            epc_output_criteria.biz_step
        )
        read_point = self._check_string(
            event.read_point,
            epc_output_criteria.read_point
        )
        source = self.check_sources(
            event,
            epc_output_criteria
        )
        destination = self.check_destinations(
            event,
            epc_output_criteria
        )
        return (event_type and action and biz_location and disposition
                and biz_step and read_point and source and destination)

    def check_sources(self, event: events.EPCISBusinessEvent,
                      epc_output_criteria: EPCISOutputCriteria):
        '''
        Loops through the sources of the event looking for any expected
        source type/id combinations.
        :param event: The event
        :param epc_output_criteria: The output criteria containing the
        expected source definition (id and type)
        :return: True or False - True if there is a matching source type/id
        combination.
        '''
        ret = False
        if epc_output_criteria.source_type and len(event.source_list) > 0:
            for source in event.source_list:
                ret = self._check_string(source.type,
                                         epc_output_criteria.source_type) and \
                      self._check_string(source.source,
                                         epc_output_criteria.source_id)
                if ret:
                    break
        return ret

    def check_destinations(self, event: events.EPCISBusinessEvent,
                           epc_output_criteria: EPCISOutputCriteria):
        '''
        Loops through the destinations of the event looking for any expected
        destination type/id combinations.
        :param event: The event
        :param epc_output_criteria: The output criteria containing the
        expected destination definition (id and type)
        :return: True or False - True if there is a matching destination type/id
        combination.
        '''
        ret = False
        if epc_output_criteria.destination_type and \
            len(event.destination_list) > 0:
            for destination in event.destination_list:
                ret = self._check_string(
                    destination.type,
                    epc_output_criteria.destination_type
                ) and \
                      self._check_string(
                          destination.destination,
                          epc_output_criteria.destination_id
                      )
                if ret:
                    break
        return ret

    def check_event_type(self, event: events.EPCISEvent, event_type: str):
        '''
        Checks the event against the expected event type.
        :param event: The event to check
        :param event_type: The expected type
        :return: True or false
        '''
        ret = False if event_type else True
        if event_type:
            if event_type == events.EventType.Transaction.value:
                ret = isinstance(event, events.TransactionEvent)
            elif event_type == events.EventType.Object.value:
                ret = isinstance(event, events.ObjectEvent)
            elif event_type == events.EventType.Aggregation.value:
                ret = isinstance(event, events.AggregationEvent)
            elif event_type == events.EventType.Transformation.value:
                ret = isinstance(event, events.TransformationEvent)
        return ret

    def check_biz_location(self, event, biz_location: str):
        '''
        Checks the event biz_location against the expected one.
        :param event: The event to check
        :param biz_location: The expected biz_location
        :return: True or False
        '''
        ret = False if biz_location else True
        if biz_location:
            ret = (biz_location == event.biz_location)
        return ret

    def check_action(self, event, action: str):
        '''
        Evaluates the event action vs. the expected action
        :param event: The event to evaluate
        :param action: The expected action
        :return: True or False (bool)
        '''
        ret = False if action else True
        if action:
            try:
                ret = (event.action == action)
            except AttributeError:
                # transformation events will not have an action
                # there is only one attribute call in that code
                # so this handler is safe
                pass
        return ret

    def _check_string(self, event_val, criteria_val):
        '''
        Checks an event value against the expected value. If the criterial
        val was not specified will return True since it's not for
        consideration.
        :param event_val: The event value.
        :param criteria_val: The expected value.
        :return: True or False
        '''
        ret = False if criteria_val else True
        if criteria_val:
            ret = (event_val == criteria_val)
        return ret

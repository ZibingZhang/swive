from enum import StrEnum


class Event(StrEnum):
    D_1_METER_DIVING = "1 Meter Diving"
    S_200_YARD_MEDLEY_RELAY = "200 Yard Medley Relay"
    S_200_YARD_FREESTYLE_RELAY = "200 Yard Freestyle Relay"
    S_400_YARD_FREESTYLE_RELAY = "400 Yard Freestyle Relay"
    S_200_YARD_INDIVIDUAL_MEDLEY = "200 Yard Individual Medley"
    S_100_YARD_BUTTERFLY = "100 Yard Butterfly"
    S_100_YARD_BACKSTROKE = "100 Yard Backstroke"
    S_100_YARD_BREASTSTROKE = "100 Yard Breaststroke"
    S_50_YARD_FREESTYLE = "50 Yard Freestyle"
    S_100_YARD_FREESTYLE = "100 Yard Freestyle"
    S_200_YARD_FREESTYLE = "200 Yard Freestyle"
    S_500_YARD_FREESTYLE = "500 Yard Freestyle"

    def as_prefix(self) -> str:
        return self.value.lower().replace(" ", "_")


INDIVIDUAL_EVENTS = {Event.D_1_METER_DIVING, Event.S_200_YARD_FREESTYLE, Event.S_200_YARD_INDIVIDUAL_MEDLEY,
                     Event.S_50_YARD_FREESTYLE, Event.S_100_YARD_BUTTERFLY, Event.S_100_YARD_FREESTYLE,
                     Event.S_500_YARD_FREESTYLE, Event.S_100_YARD_BACKSTROKE, Event.S_100_YARD_BREASTSTROKE}

RELAY_EVENTS = {Event.S_200_YARD_MEDLEY_RELAY, Event.S_200_YARD_FREESTYLE_RELAY, Event.S_400_YARD_FREESTYLE_RELAY}

EVENT_ORDER = [
    Event.D_1_METER_DIVING,
    Event.S_200_YARD_MEDLEY_RELAY,
    Event.S_200_YARD_FREESTYLE,
    Event.S_200_YARD_INDIVIDUAL_MEDLEY,
    Event.S_50_YARD_FREESTYLE,
    Event.S_100_YARD_BUTTERFLY,
    Event.S_100_YARD_FREESTYLE,
    Event.S_500_YARD_FREESTYLE,
    Event.S_200_YARD_FREESTYLE_RELAY,
    Event.S_100_YARD_BACKSTROKE,
    Event.S_100_YARD_BREASTSTROKE,
    Event.S_400_YARD_FREESTYLE_RELAY,
]

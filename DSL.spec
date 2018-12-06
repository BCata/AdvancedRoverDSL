Mission:
    Name: Exploration Mission
    DefaultSpeed: 50
    BorderColor: White
    Timeout: 300 seconds
    CreateReport

    Tasks:
        Task: find lakes
            Timeout: until termination
            SearchPolicy: colorBased
            UnkownLakePolicy: measure | avoid
            Lake:
                Color: Blue
                MeasureFeatures:
                    Feature: temperature
                    Feature: depth
                    Feature: salinity

            Lake:
                Color: Red

        Task: push light brick
            Timeout: 100 seconds
            Amount: 2

        Task: park rover

extension: .mr


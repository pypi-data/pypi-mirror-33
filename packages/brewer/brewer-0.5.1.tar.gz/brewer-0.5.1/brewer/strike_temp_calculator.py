#!/usr/bin/env python
import sys

def calc_strike_temp(WaterVolInQuarts, GrainMassInPounds, GrainTemp, MashTemp):
    """
    Calculates the proper strike water temperature for mashing. All arguments should be floats or ints
    """
    WaterToGrainRatio = WaterVolInQuarts / GrainMassInPounds
    StrikeWaterTemp = ((0.2 / WaterToGrainRatio) *
                       (MashTemp - GrainTemp)) + MashTemp
    return round(StrikeWaterTemp, 1)

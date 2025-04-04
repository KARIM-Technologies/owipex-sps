# TAOSONICFLOWUNIT Konstanten
TAOSONICFLOWUNIT_M3 = 0       # Kubikmeter (m3)
TAOSONICFLOWUNIT_LITER = 1    # Liter (L)
TAOSONICFLOWUNIT_GAL = 2      # Amerikanische Gallone (GAL)
TAOSONICFLOWUNIT_FEET3 = 3    # Kubikfuß (CF)

class UsFlowHandler:
    def __init__(self, sensor):
        self.sensor = sensor  # Übergeben Sie die PH_Sensor-Instanz

    def fetchViaDeviceManager_Helper(self, address, registerCount, dataformat, infoText):
        # get current flow
        value = self.sensor.read_register(address, registerCount, dataformat)
        if value is None:
            raise ValueError(f"Us-Flow Sensorlesung {infoText} fehlgeschlagen. Überprüfen Sie die Verbindung.")
        return value

    def calculateSumFlowValueForTaosonic(self, totalFlowUnitNumber, totalFlowMultiplier, flowValueAccumulator, flowDecimalFraction):
        # The internal accumulator is been presented by a LONG number for the integer part together
        # with a REAL number for the decimal fraction. In general uses, only the integer part needs to be read. Reading
        # the fraction can be omitted. The final accumulator result has a relation with unit and multiplier. Assume N
        # stands for the integer part (for the positive accumulator, the integer part is the content of REG 0009, 0010, a
        # 32-bits signed LONG integer,), Nf stands for the decimal fraction part (for the positive accumulator, the
        # fraction part is the content of REG 0011, 0012, a 32-bits REAL float number,), n stands for the flow decimal
        # point (REG 1439).
        # then
        # The final positive flow rate=(N+Nf ) ×10n-3 (in unit decided by REG 1439)
        # The meaning of REG 1438 which has a range of 0~3 is as following:
        #     0 cubic meter (m3)
        #     1 liter (L)
        #     2 American gallon (GAL)
        #     3 Cubic feet (CF)
        # For example, if REG0009=123456789, REG0010=0.123, and REG1439=-1, REG1438=0
        # Then the positive flow is 12345.6789123 m3

        if not isinstance(totalFlowMultiplier, int):
            raise Exception(f"invalid type for total flow multiplier: {type(totalFlowMultiplier)}")
        if totalFlowMultiplier < -4 or totalFlowMultiplier > 4:
            raise Exception(f"invalid total flow multiplier value found in Taosonic Flow Meter (see reg 1439): {totalFlowMultiplier}")

        if totalFlowUnitNumber != TAOSONICFLOWUNIT_M3 and totalFlowUnitNumber != TAOSONICFLOWUNIT_LITER and totalFlowUnitNumber != TAOSONICFLOWUNIT_GAL and totalFlowUnitNumber != TAOSONICFLOWUNIT_FEET3:
            raise Exception(f"invalid total flow unit number found in Taosonic Flow Meter (see reg 1438): {totalFlowUnitNumber}")

        flowValueAccumulatorAsFloat = float(flowValueAccumulator)
        flowValueAccumulatorWithFractionAsFloat = flowValueAccumulatorAsFloat + flowDecimalFraction

        sumFlowValue = flowValueAccumulatorWithFractionAsFloat * 10**(totalFlowMultiplier-3)
        print("calculateSumFlowValueForTaosonic, sumFlowValue: " + str(sumFlowValue))
        return sumFlowValue

    def convertFlowValueFromUnitToM3ForTaosonic(self, flowValueInUnit, unitNumber):
        if (unitNumber == TAOSONICFLOWUNIT_M3):
            return flowValueInUnit
        if (unitNumber == TAOSONICFLOWUNIT_LITER):
            return flowValueInUnit * 0.001
        if (unitNumber == TAOSONICFLOWUNIT_GAL):
            return flowValueInUnit * 0.00378541
        if (unitNumber == TAOSONICFLOWUNIT_FEET3):
            return flowValueInUnit * 0.0283168
        
        # Falls keine der bekannten Einheiten übereinstimmt
        raise Exception(f"invalid total flow unit number for Taosonic Flow Meter (see reg 1438): {unitNumber}")

    def fetchViaDeviceManager(self):
        # get current flow
        currentFlowValue = self.fetchViaDeviceManager_Helper(1, 2, ">f", "1")
        print("fetchViaDeviceManager, Stop 19, currentFlowValue: " + str(currentFlowValue))

        # get registers for overall flow sum
        totalFlowUnitNumber = self.fetchViaDeviceManager_Helper(1438, 1, ">h", "a")
        print("fetchViaDeviceManager, Stop 29a, totalFlowUnitNumber: " + str(totalFlowUnitNumber))

        totalFlowMultiplier = self.fetchViaDeviceManager_Helper(1439, 1, ">h", "b")
        print("fetchViaDeviceManager, Stop 29b, totalFlowMultiplier: " + str(totalFlowMultiplier))

        flowValueAccumulator = self.fetchViaDeviceManager_Helper(25, 2, ">l", "c")
        print("fetchViaDeviceManager, Stop 29c, flowValueAccumulator: " + str(flowValueAccumulator))

        flowDecimalFraction = self.fetchViaDeviceManager_Helper(27, 2, ">f", "d")
        print("fetchViaDeviceManager, Stop 29d, flowDecimalFraction: " + str(flowDecimalFraction))

        # calculate overall flow sum
        sumFlowValueInUnit = self.calculateSumFlowValueForTaosonic(totalFlowUnitNumber, totalFlowMultiplier, flowValueAccumulator, flowDecimalFraction)
        print("fetchViaDeviceManager, Stop 31, sumFlowValueInUnit: " + str(sumFlowValueInUnit))
        sumFlowValueInM3 = self.convertFlowValueFromUnitToM3ForTaosonic(sumFlowValueInUnit, totalFlowUnitNumber)
        print("fetchViaDeviceManager, Stop 39, sumFlowValueInM3: " + str(sumFlowValueInM3))

        print(f"fetchViaDeviceManager, Stop 99, currentFlowValue={currentFlowValue}, sumFlowValue={sumFlowValueInM3}")
        return currentFlowValue, sumFlowValueInM3
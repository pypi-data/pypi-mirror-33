from enum import IntEnum

from inoon_lora_packet.packet import Packet, HexConverter
from inoon_lora_packet.bsp.accelerometer import BMA280


class MachineState(IntEnum):
    commisioning = 0
    inactive = 1
    active = 2


class MRMeasurementV3Packet(Packet):

    def _field_spec(self):
        return [
            {'name': 'mrt_protocol_version',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'machine_state',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': [MachineState[k] for k in MachineState._member_map_]},

            {'name': 'mrt_report_period',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_report_header',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_average',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_stdev',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_min',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_max',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_runtime_duration',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_operation_threshold',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_shock_threshold',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_timestamp',
             'bytes': 4,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_battery_level',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_acc_status',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_reserved',
             'bytes': 8,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

        ]

    def __str__(self):
        msg = 'MRMeasure | '
        msg += 'Ver: {} | '.format(self.mrt_protocol_version)
        msg += 'State: {} | '.format(self.machine_state)
        msg += 'Period: {} | '.format(self.mrt_report_period)
        msg += 'Header: {} | '.format(self.mrt_report_header)
        msg += 'Avg.: {}mg | '.format(BMA280.gravity(1, self.mrt_average))
        msg += 'Std.: {}mg | '.format(BMA280.gravity(1, self.mrt_stdev))
        msg += 'Min: {}mg | '.format(BMA280.gravity(1, self.mrt_min))
        msg += 'Max: {}mg | '.format(BMA280.gravity(1, self.mrt_max))
        msg += 'RtDur.: {} | '.format(self.mrt_runtime_duration)
        msg += 'OpThr.: {} | '.format(self.mrt_operation_threshold)
        msg += 'ShkThr.: {} | '.format(self.mrt_shock_threshold)
        msg += 'Ts.: {} | '.format(self.mrt_timestamp)
        msg += 'Bat.: {} | '.format(self.mrt_battery_level)
        msg += 'Acc.: {} | '.format(self.mrt_acc_status)
        msg += 'Resv.: {}'.format(self.mrt_reserved)
        return msg

    @classmethod
    def encode(cls,
               version,
               machine_state,
               report_period,
               report_header,
               min_val,
               max_val,
               avg,
               std,
               runtime_duration,
               operation_threshold,
               shock_threshold,
               timestamp,
               battery,
               acc_status,
               resv):
        enc = ''
        enc += format(version, '02x')
        enc += format(machine_state, '02x')
        enc += format(report_period, '02x')
        enc += format(report_header, '02x')
        enc += format(avg, '04x')
        enc += format(std, '04x')
        enc += format(min_val, '04x')
        enc += format(max_val, '04x')
        enc += format(runtime_duration, '04x')
        enc += format(operation_threshold, '04x')
        enc += format(shock_threshold, '04x')
        enc += format(timestamp, '08x')
        enc += format(battery, '02x')
        enc += format(acc_status, '02x')
        enc += format(resv, '016x')

        return enc.lower()

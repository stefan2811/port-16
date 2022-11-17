from typing import Any, Optional

from pydantic.main import Enum
from pydantic import BaseModel


class ConfigKeyAccessibility(str, Enum):
    R = 'R'
    RW = 'RW'
    BOTH = 'BOTH'


class ConfigKeyType(str, Enum):
    BOOLEAN = 'BOOLEAN'
    INTEGER = 'INTEGER'
    CSL = 'CSL'


class ConfigEntry(BaseModel):
    name: str = ''
    value: Any
    default_value: Any
    value_type: ConfigKeyType.BOOLEAN
    required: bool = False
    description: str = ''
    access: ConfigKeyAccessibility = ConfigKeyAccessibility.BOTH


class ConfigEntryModel(BaseModel):
    name: str
    value: Any
    access: Optional[ConfigKeyAccessibility] = None


# Core Profile

class AllowOfflineTxForUnknownId(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = False
        super(AllowOfflineTxForUnknownId, self).__init__(
            name='AllowOfflineTxForUnknownId',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=False,
            access=ConfigKeyAccessibility.RW,
            description=(
                'If this key exists, the Charge Point supports Unknown '
                'Offline Authorization. If this key reports a value of true, '
                'Unknown Offline Authorization is enabled.'
            ),
            **kwargs
        )


class AuthorizationCacheEnabled(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = False
        super(AuthorizationCacheEnabled, self).__init__(
            name='AuthorizationCacheEnabled',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=False,
            access=ConfigKeyAccessibility.RW,
            description=(
                'If this key exists, the Charge Point supports an '
                'Authorization Cache. If this key reports a value of true, '
                'the Authorization Cache is enabled.'
            ),
            **kwargs
        )


class AuthorizeRemoteTxRequests(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = False
        super(AuthorizeRemoteTxRequests, self).__init__(
            name='AuthorizeRemoteTxRequests',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=True,
            access=ConfigKeyAccessibility.BOTH,
            description=(
                'Whether a remote request to start a transaction in the form '
                'of a RemoteStartTransaction.req message should be '
                'authorized beforehand like a local action to start a '
                'transaction.'
            ),
            **kwargs
        )


class BlinkRepeat(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 3
        super(BlinkRepeat, self).__init__(
            name='BlinkRepeat',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Number of times to blink Charge Point lighting '
                'when signalling'
            ),
            **kwargs
        )


class ClockAlignedDataInterval(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 900
        super(ClockAlignedDataInterval, self).__init__(
            name='ClockAlignedDataInterval',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Size (in seconds) of the clock-aligned data interval. This '
                'is the size (in seconds) of the set of evenly spaced '
                'aggregation intervals per day, starting at 00:00:00 '
                '(midnight). For example, a value of 900 (15 minutes) '
                'indicates that every day should be broken into 96 '
                '15-minute intervals. When clock aligned data is being '
                'transmitted, the interval in question is identified by the '
                'start time and (optional) duration interval value, '
                'represented according to the ISO8601 standard. All '
                '"per-period" data (e.g. energy readings) should be '
                'accumulated (for "flow" type measurands such as energy), '
                'or averaged (for other values) across the entire interval '
                '(or partial interval, at the beginning or end of a '
                'Transaction), and transmitted (if so enabled) at the end '
                'of each interval, bearing the interval start time '
                'timestamp. A value of "0" (numeric zero), by convention, '
                'is to be interpreted to mean that no clock-aligned data '
                'should be transmitted.'
            ),
            **kwargs
        )


class ConnectionTimeOut(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 20
        super(ConnectionTimeOut, self).__init__(
            name='ConnectionTimeOut',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Description Interval *from beginning of status: '
                '\'Preparing\' until incipient Transaction is automatically '
                'canceled, due to failure of EV driver to (correctly) insert '
                'the charging cable connector(s) into the appropriate '
                'socket(s). The Charge Point SHALL go back to the original '
                'state, probably: \'Available\'.'
            ),
            **kwargs
        )


class ConnectorPhaseRotation(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = ['STR']
        super(ConnectorPhaseRotation, self).__init__(
            name='ConnectorPhaseRotation',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.CSL,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'The phase rotation per connector in respect to the '
                'connector’s electrical meter (or if absent, the grid '
                'connection). Possible values per connector are:\n'
                'NotApplicable (for Single phase or DC Charge Points)\n'
                'Unknown (not (yet) known)\nRST (Standard Reference Phasing) '
                'RTS (Reversed Reference Phasing) SRT (Reversed 240 degree '
                'rotation) STR (Standard 120 degree rotation) TRS (Standard '
                '240 degree rotation) TSR (Reversed 120 degree rotation) '
                'R can be identified as phase 1 (L1), S as phase 2 (L2), '
                'T as phase 3 (L3). If known, the Charge Point MAY also '
                'report the phase rotation between the grid connection and '
                'the main energy meter by using index number Zero (0). Values '
                'are reported in CSL, formatted: 0.RST, 1.RST, 2.RTS'
            ),
            **kwargs
        )


class ConnectorPhaseRotationMaxLength(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(ConnectorPhaseRotationMaxLength, self).__init__(
            name='ConnectorPhaseRotationMaxLength',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of items in a ConnectorPhaseRotation '
                'Configuration Key.'
            ),
            **kwargs
        )


class GetConfigurationMaxKeys(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(GetConfigurationMaxKeys, self).__init__(
            name='GetConfigurationMaxKeys',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of requested configuration keys in a '
                'GetConfiguration.req PDU.'
            ),
            **kwargs
        )


class HeartbeatInterval(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(HeartbeatInterval, self).__init__(
            name='HeartbeatInterval',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Description Interval of inactivity (no OCPP exchanges) with '
                'central system after which the Charge Point should send a '
                'Heartbeat.req PDU'
            ),
            **kwargs
        )


class LightIntensity(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 70
        super(LightIntensity, self).__init__(
            name='LightIntensity',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Percentage of maximum intensity at which to illuminate '
                'Charge Point lighting'
            ),
            **kwargs
        )


class LocalAuthorizeOffline(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = False
        super(LocalAuthorizeOffline, self).__init__(
            name='LocalAuthorizeOffline',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'whether the Charge Point, when offline, will start a '
                'transaction for locally-authorized identifiers.'
            ),
            **kwargs
        )


class LocalPreAuthorize(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = False
        super(LocalPreAuthorize, self).__init__(
            name='LocalPreAuthorize',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'whether the Charge Point, when online, will start a '
                'transaction for locally-authorized identifiers without '
                'waiting for or requesting an Authorize.conf from the '
                'Central System'
            ),
            **kwargs
        )


class MaxEnergyOnInvalidId(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(MaxEnergyOnInvalidId, self).__init__(
            name='MaxEnergyOnInvalidId',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Maximum energy in Wh delivered when an identifier is '
                'invalidated by the Central System after start of a '
                'transaction.'
            ),
            **kwargs
        )


class MeterValuesAlignedData(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = ['']
        super(MeterValuesAlignedData, self).__init__(
            name='MeterValuesAlignedData',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.CSL,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Clock-aligned measurand(s) to be included in a '
                'MeterValues.req PDU, every ClockAlignedDataInterval seconds'
            ),
            **kwargs
        )


class MeterValuesAlignedDataMaxLength(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(MeterValuesAlignedDataMaxLength, self).__init__(
            name='MeterValuesAlignedDataMaxLength',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of items in a MeterValuesAlignedData '
                'Configuration Key.'
            ),
            **kwargs
        )


class MeterValuesSampledData(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = ['']
        super(MeterValuesSampledData, self).__init__(
            name='MeterValuesSampledData',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.CSL,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Sampled measurands to be included in a MeterValues.req PDU, '
                'every MeterValueSampleInterval seconds. Where applicable, '
                'the Measurand is combined with the optional phase; for '
                'instance: Voltage.L1\n'
                'Default: "Energy.Active.Import.Register"'
            ),
            **kwargs
        )


class MeterValuesSampledDataMaxLength(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(MeterValuesSampledDataMaxLength, self).__init__(
            name='MeterValuesSampledDataMaxLength',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of items in a MeterValuesSampledData '
                'Configuration Key.'
            ),
            **kwargs
        )


class MeterValueSampleInterval(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(MeterValueSampleInterval, self).__init__(
            name='MeterValueSampleInterval',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Interval between sampling of metering (or other) data, '
                'intended to be transmitted by "MeterValues" PDUs. For '
                'charging session data (ConnectorId>0), samples are acquired '
                'and transmitted periodically at this interval from the '
                'start of the charging transaction. A value of "0" '
                '(numeric zero), by convention, is to be interpreted '
                'to mean that no sampled data should be transmitted.'
            ),
            **kwargs
        )


class MinimumStatusDuration(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(MinimumStatusDuration, self).__init__(
            name='MinimumStatusDuration',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.RW,
            description=(
                'The minimum duration that a Charge Point or Connector '
                'status is stable before a StatusNotification.req PDU '
                'is sent to the Central System.'
            ),
            **kwargs
        )


class NumberOfConnectors(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(NumberOfConnectors, self).__init__(
            name='NumberOfConnectors',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.R,
            description=(
                'The number of physical charging connectors of '
                'this Charge Point.'
            ),
            **kwargs
        )


class ResetRetries(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 3
        super(ResetRetries, self).__init__(
            name='ResetRetries',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Number of times to retry an unsuccessful reset of '
                'the Charge Point.'
            ),
            **kwargs
        )


class StopTransactionOnEVSideDisconnect(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = True
        super(StopTransactionOnEVSideDisconnect, self).__init__(
            name='StopTransactionOnEVSideDisconnect',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'When set to true, the Charge Point SHALL administratively '
                'stop the transaction when the cable is unplugged from '
                'the EV.'
            ),
            **kwargs
        )


class StopTransactionOnInvalidId(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = True
        super(StopTransactionOnInvalidId, self).__init__(
            name='StopTransactionOnInvalidId',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'whether the Charge Point will stop an ongoing transaction '
                'when it receives a non- Accepted authorization status in '
                'a StartTransaction.conf for this transaction'
            ),
            **kwargs
        )


class StopTxnAlignedData(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = ['']
        super(StopTxnAlignedData, self).__init__(
            name='StopTxnAlignedData',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.CSL,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Clock-aligned periodic measurand(s) to be included in '
                'the TransactionData element of StopTransaction.req '
                'MeterValues.req PDU for every ClockAlignedDataInterval '
                'of the Transaction'
            ),
            **kwargs
        )


class StopTxnAlignedDataMaxLength(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(StopTxnAlignedDataMaxLength, self).__init__(
            name='StopTxnAlignedDataMaxLength',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of items in a StopTxnAlignedData '
                'Configuration Key.'
            ),
            **kwargs
        )


class StopTxnSampledData(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = ['']
        super(StopTxnSampledData, self).__init__(
            name='StopTxnSampledData',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.CSL,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Sampled measurands to be included in the TransactionData '
                'element of StopTransaction.req PDU, every '
                'MeterValueSampleInterval seconds from the start of '
                'the charging session'
            ),
            **kwargs
        )


class StopTxnSampledDataMaxLength(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(StopTxnSampledDataMaxLength, self).__init__(
            name='StopTxnSampledData',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of items in a StopTxnSampledData '
                'Configuration Key.'
            ),
            **kwargs
        )


class SupportedFeatureProfiles(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = [
            'Core', 'FirmwareManagement'
        ]
        super(SupportedFeatureProfiles, self).__init__(
            name='SupportedFeatureProfiles',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.CSL,
            required=True,
            access=ConfigKeyAccessibility.R,
            description=(
                'A list of supported Feature Profiles. Possible profile '
                'identifiers: Core, FirmwareManagement, '
                'LocalAuthListManagement, Reservation, '
                'SmartCharging and RemoteTrigger.'
            ),
            **kwargs
        )


class SupportedFeatureProfilesMaxLength(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(SupportedFeatureProfilesMaxLength, self).__init__(
            name='SupportedFeatureProfilesMaxLength',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of items in a SupportedFeatureProfiles '
                'Configuration Key.'
            ),
            **kwargs
        )


class TransactionMessageAttempts(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(TransactionMessageAttempts, self).__init__(
            name='TransactionMessageAttempts',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'How often the Charge Point should try to submit a '
                'transaction-related message when the Central System '
                'fails to process it.'
            ),
            **kwargs
        )


class TransactionMessageRetryInterval(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(TransactionMessageRetryInterval, self).__init__(
            name='TransactionMessageRetryInterval',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'How long the Charge Point should wait before '
                'resubmitting a transaction-related message that the '
                'Central System failed to process.'
            ),
            **kwargs
        )


class UnlockConnectorOnEVSideDisconnect(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = False
        super(UnlockConnectorOnEVSideDisconnect, self).__init__(
            name='UnlockConnectorOnEVSideDisconnect',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'When set to true, the Charge Point SHALL unlock the cable '
                'on Charge Point side when the cable is unplugged at the EV.'
            ),
            **kwargs
        )


class WebSocketPingInterval(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(WebSocketPingInterval, self).__init__(
            name='WebSocketPingInterval',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=False,
            access=ConfigKeyAccessibility.RW,
            description=(
                'Only relevant for websocket implementations. 0 disables '
                'client side websocket Ping/Pong. In this case there is '
                'either no ping/pong or the server initiates the ping '
                'and client responds with Pong. Positive values are '
                'interpreted as number of seconds between pings. Negative '
                'values are not allowed. ChangeConfiguration is expected '
                'to return a REJECTED result.'
            ),
            **kwargs
        )


# Local Auth List Management Profile

class LocalAuthListEnabled(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = False
        super(LocalAuthListEnabled, self).__init__(
            name='LocalAuthListEnabled',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=True,
            access=ConfigKeyAccessibility.RW,
            description=(
                'whether the Local Authorization List is enabled'
            ),
            **kwargs
        )


class LocalAuthListMaxLength(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(LocalAuthListMaxLength, self).__init__(
            name='LocalAuthListMaxLength',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of identifications that can be stored in '
                'the Local Authorization List'
            ),
            **kwargs
        )


class SendLocalListMaxLength(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(SendLocalListMaxLength, self).__init__(
            name='SendLocalListMaxLength',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of identifications that can be send in a '
                'single SendLocalList.req'
            ),
            **kwargs
        )


# Reservation Profile

class ReserveConnectorZeroSupported(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = False
        super(ReserveConnectorZeroSupported, self).__init__(
            name='SendLocalListMaxLength',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=False,
            access=ConfigKeyAccessibility.R,
            description=(
                'If this configuration key is present and set to true: '
                'Charge Point support reservations on connector 0.'
            ),
            **kwargs
        )


# Smart Charging Profile

class ChargeProfileMaxStackLevel(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(ChargeProfileMaxStackLevel, self).__init__(
            name='ChargeProfileMaxStackLevel',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.R,
            description=(
                'Max StackLevel of a ChargingProfile. The number defined '
                'also indicates the max allowed number of installed '
                'charging schedules per Charging Profile Purposes.'
            ),
            **kwargs
        )


class ChargingScheduleAllowedChargingRateUnit(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = ['Current', 'Power']
        super(ChargingScheduleAllowedChargingRateUnit, self).__init__(
            name='ChargingScheduleAllowedChargingRateUnit',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.CSL,
            required=True,
            access=ConfigKeyAccessibility.R,
            description=(
                'A list of supported quantities for use in a '
                'ChargingSchedule. Allowed values: \'Current\' and \'Power\''
            ),
            **kwargs
        )


class ChargingScheduleMaxPeriods(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 10
        super(ChargingScheduleMaxPeriods, self).__init__(
            name='ChargingScheduleMaxPeriods',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of periods that may be defined '
                'per ChargingSchedule.'
            ),
            **kwargs
        )


class ConnectorSwitch3to1PhaseSupported(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = False
        super(ConnectorSwitch3to1PhaseSupported, self).__init__(
            name='ConnectorSwitch3to1PhaseSupported',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.BOOLEAN,
            required=False,
            access=ConfigKeyAccessibility.R,
            description=(
                'If defined and true, this Charge Point support '
                'switching from 3 to 1 phase during a Transaction.'
            ),
            **kwargs
        )


class MaxChargingProfilesInstalled(ConfigEntry):
    def __init__(self, value=None, **kwargs):
        default_value = 3
        super(MaxChargingProfilesInstalled, self).__init__(
            name='MaxChargingProfilesInstalled',
            value=value or default_value,
            default_value=default_value,
            value_type=ConfigKeyType.INTEGER,
            required=True,
            access=ConfigKeyAccessibility.R,
            description=(
                'Maximum number of Charging profiles installed at a time'
            ),
            **kwargs
        )


def get_all():
    """
    Returns all configuration objects, objects that are subclasses of
    ConfigEntry class.

    :return: List of objects that are subclasses of ConfigEntry class.
    """
    return [cls() for cls in ConfigEntry.__subclasses__()]

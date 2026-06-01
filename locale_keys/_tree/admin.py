"""Auto-generated locale tree: admin. Do not edit."""
from __future__ import annotations

from dataclasses import dataclass

from locale_keys.types import LocalizedString, ResolveMap


@dataclass(frozen=True, slots=True)
class Admin:
    description: LocalizedString
    name: LocalizedString
    addrole: AdminAddrole
    ban: AdminBan
    boosterrole: AdminBoosterrole
    channels: AdminChannels
    copy7tv: AdminCopy7tv
    copyemoji: AdminCopyemoji
    copyrole: AdminCopyrole
    createemoji: AdminCreateemoji
    createrole: AdminCreaterole
    createticket: AdminCreateticket
    deleterole: AdminDeleterole
    embed: AdminEmbed
    emoji: AdminEmoji
    jointocreate: AdminJointocreate
    jtc: AdminJtc
    kick: AdminKick
    localegroup: AdminLocalegroup
    lock: AdminLock
    messaging: AdminMessaging
    moderation: AdminModeration
    moverole: AdminMoverole
    nickname: AdminNickname
    nuke: AdminNuke
    purge: AdminPurge
    purgegroup: AdminPurgegroup
    removerole: AdminRemoverole
    removetimeout: AdminRemovetimeout
    report: AdminReport
    role: AdminRole
    rolemanage: AdminRolemanage
    rps: AdminRps
    say: AdminSay
    setlocale: AdminSetlocale
    setup: AdminSetup
    slowmode: AdminSlowmode
    timeout: AdminTimeout
    tm: AdminTm
    triggermessages: AdminTriggermessages
    unban: AdminUnban
    unlock: AdminUnlock
    warn: AdminWarn

@dataclass(frozen=True, slots=True)
class AdminAddrole:
    description: LocalizedString
    name: LocalizedString
    params: AdminAddroleParams

@dataclass(frozen=True, slots=True)
class AdminBan:
    description: LocalizedString
    name: LocalizedString
    params: AdminBanParams

@dataclass(frozen=True, slots=True)
class AdminBoosterrole:
    description: LocalizedString
    name: LocalizedString
    params: AdminBoosterroleParams

@dataclass(frozen=True, slots=True)
class AdminCopy7tv:
    description: LocalizedString
    name: LocalizedString
    params: AdminCopy7tvParams

@dataclass(frozen=True, slots=True)
class AdminCopyemoji:
    description: LocalizedString
    name: LocalizedString
    params: AdminCopyemojiParams

@dataclass(frozen=True, slots=True)
class AdminCopyrole:
    description: LocalizedString
    name: LocalizedString
    params: AdminCopyroleParams

@dataclass(frozen=True, slots=True)
class AdminCreateemoji:
    description: LocalizedString
    name: LocalizedString
    params: AdminCreateemojiParams

@dataclass(frozen=True, slots=True)
class AdminCreaterole:
    description: LocalizedString
    name: LocalizedString
    params: AdminCreateroleParams

@dataclass(frozen=True, slots=True)
class AdminCreateticket:
    description: LocalizedString
    name: LocalizedString
    params: AdminCreateticketParams

@dataclass(frozen=True, slots=True)
class AdminDeleterole:
    description: LocalizedString
    name: LocalizedString
    params: AdminDeleteroleParams

@dataclass(frozen=True, slots=True)
class AdminEmbed:
    description: LocalizedString
    name: LocalizedString
    params: AdminEmbedParams

@dataclass(frozen=True, slots=True)
class AdminJtc:
    removechannel: AdminJtcRemovechannel
    setchannel: AdminJtcSetchannel

@dataclass(frozen=True, slots=True)
class AdminKick:
    description: LocalizedString
    name: LocalizedString
    params: AdminKickParams

@dataclass(frozen=True, slots=True)
class AdminLock:
    description: LocalizedString
    name: LocalizedString
    params: AdminLockParams

@dataclass(frozen=True, slots=True)
class AdminMoverole:
    description: LocalizedString
    name: LocalizedString
    params: AdminMoveroleParams

@dataclass(frozen=True, slots=True)
class AdminNickname:
    description: LocalizedString
    name: LocalizedString
    params: AdminNicknameParams

@dataclass(frozen=True, slots=True)
class AdminNuke:
    description: LocalizedString
    name: LocalizedString
    params: AdminNukeParams

@dataclass(frozen=True, slots=True)
class AdminPurge:
    description: LocalizedString
    name: LocalizedString
    params: AdminPurgeParams

@dataclass(frozen=True, slots=True)
class AdminRemoverole:
    description: LocalizedString
    name: LocalizedString
    params: AdminRemoveroleParams

@dataclass(frozen=True, slots=True)
class AdminRemovetimeout:
    description: LocalizedString
    name: LocalizedString
    params: AdminRemovetimeoutParams

@dataclass(frozen=True, slots=True)
class AdminRps:
    removechannel: AdminRpsRemovechannel
    setchannel: AdminRpsSetchannel
    showreports: AdminRpsShowreports
    unblockreporter: AdminRpsUnblockreporter

@dataclass(frozen=True, slots=True)
class AdminSay:
    description: LocalizedString
    name: LocalizedString
    params: AdminSayParams

@dataclass(frozen=True, slots=True)
class AdminSetlocale:
    description: LocalizedString
    name: LocalizedString
    params: AdminSetlocaleParams

@dataclass(frozen=True, slots=True)
class AdminSlowmode:
    description: LocalizedString
    name: LocalizedString
    params: AdminSlowmodeParams

@dataclass(frozen=True, slots=True)
class AdminTimeout:
    description: LocalizedString
    name: LocalizedString
    params: AdminTimeoutParams

@dataclass(frozen=True, slots=True)
class AdminTm:
    add: AdminTmAdd
    configure: AdminTmConfigure

@dataclass(frozen=True, slots=True)
class AdminTriggermessages:
    description: LocalizedString
    name: LocalizedString
    params: AdminTriggermessagesParams

@dataclass(frozen=True, slots=True)
class AdminUnban:
    description: LocalizedString
    name: LocalizedString
    params: AdminUnbanParams

@dataclass(frozen=True, slots=True)
class AdminUnlock:
    description: LocalizedString
    name: LocalizedString
    params: AdminUnlockParams

@dataclass(frozen=True, slots=True)
class AdminWarn:
    description: LocalizedString
    name: LocalizedString
    add: AdminWarnAdd
    config: AdminWarnConfig
    view: AdminWarnView

@dataclass(frozen=True, slots=True)
class AdminJointocreate:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminReport:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRole:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminModeration:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminChannels:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminMessaging:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminEmoji:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminSetup:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRolemanage:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminPurgegroup:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminLocalegroup:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminAddroleParams:
    role: AdminAddroleParamsRole
    user: AdminAddroleParamsUser

@dataclass(frozen=True, slots=True)
class AdminBanParams:
    deletemessagedays: AdminBanParamsDeletemessagedays
    reason: AdminBanParamsReason
    user: AdminBanParamsUser

@dataclass(frozen=True, slots=True)
class AdminBoosterroleParams:
    role: AdminBoosterroleParamsRole

@dataclass(frozen=True, slots=True)
class AdminCopy7tvParams:
    twitch: AdminCopy7tvParamsTwitch

@dataclass(frozen=True, slots=True)
class AdminCopyemojiParams:
    emoji: AdminCopyemojiParamsEmoji

@dataclass(frozen=True, slots=True)
class AdminCopyroleParams:
    copymembers: AdminCopyroleParamsCopymembers
    role: AdminCopyroleParamsRole

@dataclass(frozen=True, slots=True)
class AdminCreateemojiParams:
    imageUrl: AdminCreateemojiParamsImageUrl
    name: AdminCreateemojiParamsName
    roles: AdminCreateemojiParamsRoles

@dataclass(frozen=True, slots=True)
class AdminCreateroleParams:
    color: AdminCreateroleParamsColor
    displayemoji: AdminCreateroleParamsDisplayemoji
    displayicon: AdminCreateroleParamsDisplayicon
    hoist: AdminCreateroleParamsHoist
    mentionable: AdminCreateroleParamsMentionable
    name: AdminCreateroleParamsName
    reason: AdminCreateroleParamsReason

@dataclass(frozen=True, slots=True)
class AdminCreateticketParams:
    channel: AdminCreateticketParamsChannel
    description: AdminCreateticketParamsDescription
    introduction: AdminCreateticketParamsIntroduction
    name: AdminCreateticketParamsName
    pingrole: AdminCreateticketParamsPingrole
    summarychannel: AdminCreateticketParamsSummarychannel

@dataclass(frozen=True, slots=True)
class AdminDeleteroleParams:
    reason: AdminDeleteroleParamsReason
    role: AdminDeleteroleParamsRole

@dataclass(frozen=True, slots=True)
class AdminEmbedParams:
    channel: AdminEmbedParamsChannel
    title: AdminEmbedParamsTitle

@dataclass(frozen=True, slots=True)
class AdminJtcRemovechannel:
    description: LocalizedString
    name: LocalizedString
    params: AdminJtcRemovechannelParams

@dataclass(frozen=True, slots=True)
class AdminJtcSetchannel:
    description: LocalizedString
    name: LocalizedString
    params: AdminJtcSetchannelParams

@dataclass(frozen=True, slots=True)
class AdminKickParams:
    reason: AdminKickParamsReason
    user: AdminKickParamsUser

@dataclass(frozen=True, slots=True)
class AdminLockParams:
    channel: AdminLockParamsChannel

@dataclass(frozen=True, slots=True)
class AdminMoveroleParams:
    copymembers: AdminMoveroleParamsCopymembers
    position: AdminMoveroleParamsPosition
    role: AdminMoveroleParamsRole
    targetrole: AdminMoveroleParamsTargetrole

@dataclass(frozen=True, slots=True)
class AdminNicknameParams:
    member: AdminNicknameParamsMember
    nickname: AdminNicknameParamsNickname

@dataclass(frozen=True, slots=True)
class AdminNukeParams:
    channel: AdminNukeParamsChannel

@dataclass(frozen=True, slots=True)
class AdminPurgeParams:
    amount: AdminPurgeParamsAmount
    channel: AdminPurgeParamsChannel
    setting: AdminPurgeParamsSetting

@dataclass(frozen=True, slots=True)
class AdminRemoveroleParams:
    role: AdminRemoveroleParamsRole
    user: AdminRemoveroleParamsUser

@dataclass(frozen=True, slots=True)
class AdminRemovetimeoutParams:
    member: AdminRemovetimeoutParamsMember
    reason: AdminRemovetimeoutParamsReason

@dataclass(frozen=True, slots=True)
class AdminRpsSetchannel:
    description: LocalizedString
    name: LocalizedString
    params: AdminRpsSetchannelParams

@dataclass(frozen=True, slots=True)
class AdminRpsShowreports:
    description: LocalizedString
    name: LocalizedString
    params: AdminRpsShowreportsParams

@dataclass(frozen=True, slots=True)
class AdminRpsUnblockreporter:
    description: LocalizedString
    name: LocalizedString
    params: AdminRpsUnblockreporterParams

@dataclass(frozen=True, slots=True)
class AdminRpsRemovechannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminSayParams:
    channel: AdminSayParamsChannel
    message: AdminSayParamsMessage

@dataclass(frozen=True, slots=True)
class AdminSetlocaleParams:
    locale: AdminSetlocaleParamsLocale

@dataclass(frozen=True, slots=True)
class AdminSlowmodeParams:
    channel: AdminSlowmodeParamsChannel
    seconds: AdminSlowmodeParamsSeconds

@dataclass(frozen=True, slots=True)
class AdminTimeoutParams:
    duration: AdminTimeoutParamsDuration
    member: AdminTimeoutParamsMember
    reason: AdminTimeoutParamsReason

@dataclass(frozen=True, slots=True)
class AdminTmAdd:
    description: LocalizedString
    name: LocalizedString
    params: AdminTmAddParams

@dataclass(frozen=True, slots=True)
class AdminTmConfigure:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminTriggermessagesParams:
    message: AdminTriggermessagesParamsMessage

@dataclass(frozen=True, slots=True)
class AdminUnbanParams:
    reason: AdminUnbanParamsReason
    username: AdminUnbanParamsUsername

@dataclass(frozen=True, slots=True)
class AdminUnlockParams:
    channel: AdminUnlockParamsChannel

@dataclass(frozen=True, slots=True)
class AdminWarnAdd:
    description: LocalizedString
    name: LocalizedString
    params: AdminWarnAddParams

@dataclass(frozen=True, slots=True)
class AdminWarnView:
    description: LocalizedString
    name: LocalizedString
    params: AdminWarnViewParams

@dataclass(frozen=True, slots=True)
class AdminWarnConfig:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminAddroleParamsRole:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminAddroleParamsUser:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminBanParamsDeletemessagedays:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminBanParamsReason:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminBanParamsUser:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminBoosterroleParamsRole:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCopy7tvParamsTwitch:
    username: AdminCopy7tvParamsTwitchUsername

@dataclass(frozen=True, slots=True)
class AdminCopyemojiParamsEmoji:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCopyroleParamsCopymembers:
    description: LocalizedString
    false: LocalizedString
    name: LocalizedString
    true: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCopyroleParamsRole:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateemojiParamsImageUrl:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateemojiParamsName:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateemojiParamsRoles:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateroleParamsColor:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateroleParamsDisplayemoji:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateroleParamsDisplayicon:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateroleParamsHoist:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateroleParamsMentionable:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateroleParamsName:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateroleParamsReason:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateticketParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateticketParamsDescription:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateticketParamsIntroduction:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateticketParamsName:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateticketParamsPingrole:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminCreateticketParamsSummarychannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminDeleteroleParamsReason:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminDeleteroleParamsRole:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminEmbedParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminEmbedParamsTitle:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminJtcRemovechannelParams:
    channel: AdminJtcRemovechannelParamsChannel

@dataclass(frozen=True, slots=True)
class AdminJtcSetchannelParams:
    channel: AdminJtcSetchannelParamsChannel

@dataclass(frozen=True, slots=True)
class AdminKickParamsReason:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminKickParamsUser:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminLockParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminMoveroleParamsPosition:
    above: LocalizedString
    below: LocalizedString
    description: LocalizedString
    name: LocalizedString
    above: AdminMoveroleParamsPositionAbove
    below: AdminMoveroleParamsPositionBelow

@dataclass(frozen=True, slots=True)
class AdminMoveroleParamsCopymembers:
    false: LocalizedString
    true: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminMoveroleParamsRole:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminMoveroleParamsTargetrole:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminNicknameParamsMember:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminNicknameParamsNickname:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminNukeParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminPurgeParamsAmount:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminPurgeParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminPurgeParamsSetting:
    all: LocalizedString
    bot: LocalizedString
    botNotPinned: LocalizedString
    description: LocalizedString
    embeds: LocalizedString
    files: LocalizedString
    notAdmin: LocalizedString
    notAdminNotPinned: LocalizedString
    notPinned: LocalizedString
    notUserAdmin: LocalizedString
    user: LocalizedString
    userNotPinned: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRemoveroleParamsRole:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRemoveroleParamsUser:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRemovetimeoutParamsMember:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRemovetimeoutParamsReason:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRpsSetchannelParams:
    channel: AdminRpsSetchannelParamsChannel

@dataclass(frozen=True, slots=True)
class AdminRpsShowreportsParams:
    user: AdminRpsShowreportsParamsUser

@dataclass(frozen=True, slots=True)
class AdminRpsUnblockreporterParams:
    user: AdminRpsUnblockreporterParamsUser

@dataclass(frozen=True, slots=True)
class AdminSayParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminSayParamsMessage:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminSetlocaleParamsLocale:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminSlowmodeParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminSlowmodeParamsSeconds:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminTimeoutParamsDuration:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminTimeoutParamsMember:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminTimeoutParamsReason:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminTmAddParams:
    casesensitive: AdminTmAddParamsCasesensitive
    response: AdminTmAddParamsResponse
    trigger: AdminTmAddParamsTrigger

@dataclass(frozen=True, slots=True)
class AdminTriggermessagesParamsMessage:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminUnbanParamsReason:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminUnbanParamsUsername:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminUnlockParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminWarnAddParams:
    member: AdminWarnAddParamsMember
    reason: AdminWarnAddParamsReason

@dataclass(frozen=True, slots=True)
class AdminWarnViewParams:
    member: AdminWarnViewParamsMember

@dataclass(frozen=True, slots=True)
class AdminCopy7tvParamsTwitchUsername:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminJtcRemovechannelParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminJtcSetchannelParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminMoveroleParamsPositionAbove:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminMoveroleParamsPositionBelow:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRpsSetchannelParamsChannel:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRpsShowreportsParamsUser:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminRpsUnblockreporterParamsUser:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminTmAddParamsCasesensitive:
    description: LocalizedString
    false: LocalizedString
    name: LocalizedString
    true: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminTmAddParamsResponse:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminTmAddParamsTrigger:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminWarnAddParamsMember:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminWarnAddParamsReason:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class AdminWarnViewParamsMember:
    description: LocalizedString

def build_admin() -> Admin:
    _n_admin_addrole_params_role = AdminAddroleParamsRole(
        description=LocalizedString('admin.addrole.params.role.description'),
        name=LocalizedString('admin.addrole.params.role.name'),
    )
    _n_admin_addrole_params_user = AdminAddroleParamsUser(
        description=LocalizedString('admin.addrole.params.user.description'),
        name=LocalizedString('admin.addrole.params.user.name'),
    )
    _n_admin_addrole_params = AdminAddroleParams(
        role=_n_admin_addrole_params_role,
        user=_n_admin_addrole_params_user,
    )
    _n_admin_addrole = AdminAddrole(
        description=LocalizedString('admin.addrole.description'),
        name=LocalizedString('admin.addrole.name'),
        params=_n_admin_addrole_params,
    )
    _n_admin_ban_params_deletemessagedays = AdminBanParamsDeletemessagedays(
        description=LocalizedString('admin.ban.params.deletemessagedays.description'),
        name=LocalizedString('admin.ban.params.deletemessagedays.name'),
    )
    _n_admin_ban_params_reason = AdminBanParamsReason(
        description=LocalizedString('admin.ban.params.reason.description'),
        name=LocalizedString('admin.ban.params.reason.name'),
    )
    _n_admin_ban_params_user = AdminBanParamsUser(
        description=LocalizedString('admin.ban.params.user.description'),
        name=LocalizedString('admin.ban.params.user.name'),
    )
    _n_admin_ban_params = AdminBanParams(
        deletemessagedays=_n_admin_ban_params_deletemessagedays,
        reason=_n_admin_ban_params_reason,
        user=_n_admin_ban_params_user,
    )
    _n_admin_ban = AdminBan(
        description=LocalizedString('admin.ban.description'),
        name=LocalizedString('admin.ban.name'),
        params=_n_admin_ban_params,
    )
    _n_admin_boosterrole_params_role = AdminBoosterroleParamsRole(
        description=LocalizedString('admin.boosterrole.params.role.description'),
    )
    _n_admin_boosterrole_params = AdminBoosterroleParams(
        role=_n_admin_boosterrole_params_role,
    )
    _n_admin_boosterrole = AdminBoosterrole(
        description=LocalizedString('admin.boosterrole.description'),
        name=LocalizedString('admin.boosterrole.name'),
        params=_n_admin_boosterrole_params,
    )
    _n_admin_channels = AdminChannels(
        description=LocalizedString('admin.channels.description'),
        name=LocalizedString('admin.channels.name'),
    )
    _n_admin_copy7tv_params_twitch_username = AdminCopy7tvParamsTwitchUsername(
        description=LocalizedString('admin.copy7tv.params.twitch.username.description'),
        name=LocalizedString('admin.copy7tv.params.twitch.username.name'),
    )
    _n_admin_copy7tv_params_twitch = AdminCopy7tvParamsTwitch(
        username=_n_admin_copy7tv_params_twitch_username,
    )
    _n_admin_copy7tv_params = AdminCopy7tvParams(
        twitch=_n_admin_copy7tv_params_twitch,
    )
    _n_admin_copy7tv = AdminCopy7tv(
        description=LocalizedString('admin.copy7tv.description'),
        name=LocalizedString('admin.copy7tv.name'),
        params=_n_admin_copy7tv_params,
    )
    _n_admin_copyemoji_params_emoji = AdminCopyemojiParamsEmoji(
        description=LocalizedString('admin.copyemoji.params.emoji.description'),
    )
    _n_admin_copyemoji_params = AdminCopyemojiParams(
        emoji=_n_admin_copyemoji_params_emoji,
    )
    _n_admin_copyemoji = AdminCopyemoji(
        description=LocalizedString('admin.copyemoji.description'),
        name=LocalizedString('admin.copyemoji.name'),
        params=_n_admin_copyemoji_params,
    )
    _n_admin_copyrole_params_copymembers = AdminCopyroleParamsCopymembers(
        description=LocalizedString('admin.copyrole.params.copymembers.description'),
        false=LocalizedString('admin.copyrole.params.copymembers.false'),
        name=LocalizedString('admin.copyrole.params.copymembers.name'),
        true=LocalizedString('admin.copyrole.params.copymembers.true'),
    )
    _n_admin_copyrole_params_role = AdminCopyroleParamsRole(
        description=LocalizedString('admin.copyrole.params.role.description'),
        name=LocalizedString('admin.copyrole.params.role.name'),
    )
    _n_admin_copyrole_params = AdminCopyroleParams(
        copymembers=_n_admin_copyrole_params_copymembers,
        role=_n_admin_copyrole_params_role,
    )
    _n_admin_copyrole = AdminCopyrole(
        description=LocalizedString('admin.copyrole.description'),
        name=LocalizedString('admin.copyrole.name'),
        params=_n_admin_copyrole_params,
    )
    _n_admin_createemoji_params_imageUrl = AdminCreateemojiParamsImageUrl(
        description=LocalizedString('admin.createemoji.params.imageUrl.description'),
        name=LocalizedString('admin.createemoji.params.imageUrl.name'),
    )
    _n_admin_createemoji_params_name = AdminCreateemojiParamsName(
        description=LocalizedString('admin.createemoji.params.name.description'),
        name=LocalizedString('admin.createemoji.params.name.name'),
    )
    _n_admin_createemoji_params_roles = AdminCreateemojiParamsRoles(
        description=LocalizedString('admin.createemoji.params.roles.description'),
        name=LocalizedString('admin.createemoji.params.roles.name'),
    )
    _n_admin_createemoji_params = AdminCreateemojiParams(
        imageUrl=_n_admin_createemoji_params_imageUrl,
        name=_n_admin_createemoji_params_name,
        roles=_n_admin_createemoji_params_roles,
    )
    _n_admin_createemoji = AdminCreateemoji(
        description=LocalizedString('admin.createemoji.description'),
        name=LocalizedString('admin.createemoji.name'),
        params=_n_admin_createemoji_params,
    )
    _n_admin_createrole_params_color = AdminCreateroleParamsColor(
        description=LocalizedString('admin.createrole.params.color.description'),
        name=LocalizedString('admin.createrole.params.color.name'),
    )
    _n_admin_createrole_params_displayemoji = AdminCreateroleParamsDisplayemoji(
        description=LocalizedString('admin.createrole.params.displayemoji.description'),
        name=LocalizedString('admin.createrole.params.displayemoji.name'),
    )
    _n_admin_createrole_params_displayicon = AdminCreateroleParamsDisplayicon(
        description=LocalizedString('admin.createrole.params.displayicon.description'),
        name=LocalizedString('admin.createrole.params.displayicon.name'),
    )
    _n_admin_createrole_params_hoist = AdminCreateroleParamsHoist(
        description=LocalizedString('admin.createrole.params.hoist.description'),
        name=LocalizedString('admin.createrole.params.hoist.name'),
    )
    _n_admin_createrole_params_mentionable = AdminCreateroleParamsMentionable(
        description=LocalizedString('admin.createrole.params.mentionable.description'),
        name=LocalizedString('admin.createrole.params.mentionable.name'),
    )
    _n_admin_createrole_params_name = AdminCreateroleParamsName(
        description=LocalizedString('admin.createrole.params.name.description'),
        name=LocalizedString('admin.createrole.params.name.name'),
    )
    _n_admin_createrole_params_reason = AdminCreateroleParamsReason(
        description=LocalizedString('admin.createrole.params.reason.description'),
        name=LocalizedString('admin.createrole.params.reason.name'),
    )
    _n_admin_createrole_params = AdminCreateroleParams(
        color=_n_admin_createrole_params_color,
        displayemoji=_n_admin_createrole_params_displayemoji,
        displayicon=_n_admin_createrole_params_displayicon,
        hoist=_n_admin_createrole_params_hoist,
        mentionable=_n_admin_createrole_params_mentionable,
        name=_n_admin_createrole_params_name,
        reason=_n_admin_createrole_params_reason,
    )
    _n_admin_createrole = AdminCreaterole(
        description=LocalizedString('admin.createrole.description'),
        name=LocalizedString('admin.createrole.name'),
        params=_n_admin_createrole_params,
    )
    _n_admin_createticket_params_channel = AdminCreateticketParamsChannel(
        description=LocalizedString('admin.createticket.params.channel.description'),
        name=LocalizedString('admin.createticket.params.channel.name'),
    )
    _n_admin_createticket_params_description = AdminCreateticketParamsDescription(
        description=LocalizedString('admin.createticket.params.description.description'),
        name=LocalizedString('admin.createticket.params.description.name'),
    )
    _n_admin_createticket_params_introduction = AdminCreateticketParamsIntroduction(
        description=LocalizedString('admin.createticket.params.introduction.description'),
        name=LocalizedString('admin.createticket.params.introduction.name'),
    )
    _n_admin_createticket_params_name = AdminCreateticketParamsName(
        description=LocalizedString('admin.createticket.params.name.description'),
        name=LocalizedString('admin.createticket.params.name.name'),
    )
    _n_admin_createticket_params_pingrole = AdminCreateticketParamsPingrole(
        description=LocalizedString('admin.createticket.params.pingrole.description'),
        name=LocalizedString('admin.createticket.params.pingrole.name'),
    )
    _n_admin_createticket_params_summarychannel = AdminCreateticketParamsSummarychannel(
        description=LocalizedString('admin.createticket.params.summarychannel.description'),
        name=LocalizedString('admin.createticket.params.summarychannel.name'),
    )
    _n_admin_createticket_params = AdminCreateticketParams(
        channel=_n_admin_createticket_params_channel,
        description=_n_admin_createticket_params_description,
        introduction=_n_admin_createticket_params_introduction,
        name=_n_admin_createticket_params_name,
        pingrole=_n_admin_createticket_params_pingrole,
        summarychannel=_n_admin_createticket_params_summarychannel,
    )
    _n_admin_createticket = AdminCreateticket(
        description=LocalizedString('admin.createticket.description'),
        name=LocalizedString('admin.createticket.name'),
        params=_n_admin_createticket_params,
    )
    _n_admin_deleterole_params_reason = AdminDeleteroleParamsReason(
        description=LocalizedString('admin.deleterole.params.reason.description'),
        name=LocalizedString('admin.deleterole.params.reason.name'),
    )
    _n_admin_deleterole_params_role = AdminDeleteroleParamsRole(
        description=LocalizedString('admin.deleterole.params.role.description'),
        name=LocalizedString('admin.deleterole.params.role.name'),
    )
    _n_admin_deleterole_params = AdminDeleteroleParams(
        reason=_n_admin_deleterole_params_reason,
        role=_n_admin_deleterole_params_role,
    )
    _n_admin_deleterole = AdminDeleterole(
        description=LocalizedString('admin.deleterole.description'),
        name=LocalizedString('admin.deleterole.name'),
        params=_n_admin_deleterole_params,
    )
    _n_admin_embed_params_channel = AdminEmbedParamsChannel(
        description=LocalizedString('admin.embed.params.channel.description'),
        name=LocalizedString('admin.embed.params.channel.name'),
    )
    _n_admin_embed_params_title = AdminEmbedParamsTitle(
        description=LocalizedString('admin.embed.params.title.description'),
        name=LocalizedString('admin.embed.params.title.name'),
    )
    _n_admin_embed_params = AdminEmbedParams(
        channel=_n_admin_embed_params_channel,
        title=_n_admin_embed_params_title,
    )
    _n_admin_embed = AdminEmbed(
        description=LocalizedString('admin.embed.description'),
        name=LocalizedString('admin.embed.name'),
        params=_n_admin_embed_params,
    )
    _n_admin_emoji = AdminEmoji(
        description=LocalizedString('admin.emoji.description'),
        name=LocalizedString('admin.emoji.name'),
    )
    _n_admin_jointocreate = AdminJointocreate(
        description=LocalizedString('admin.jointocreate.description'),
        name=LocalizedString('admin.jointocreate.name'),
    )
    _n_admin_jtc_removechannel_params_channel = AdminJtcRemovechannelParamsChannel(
        description=LocalizedString('admin.jtc.removechannel.params.channel.description'),
        name=LocalizedString('admin.jtc.removechannel.params.channel.name'),
    )
    _n_admin_jtc_removechannel_params = AdminJtcRemovechannelParams(
        channel=_n_admin_jtc_removechannel_params_channel,
    )
    _n_admin_jtc_removechannel = AdminJtcRemovechannel(
        description=LocalizedString('admin.jtc.removechannel.description'),
        name=LocalizedString('admin.jtc.removechannel.name'),
        params=_n_admin_jtc_removechannel_params,
    )
    _n_admin_jtc_setchannel_params_channel = AdminJtcSetchannelParamsChannel(
        description=LocalizedString('admin.jtc.setchannel.params.channel.description'),
        name=LocalizedString('admin.jtc.setchannel.params.channel.name'),
    )
    _n_admin_jtc_setchannel_params = AdminJtcSetchannelParams(
        channel=_n_admin_jtc_setchannel_params_channel,
    )
    _n_admin_jtc_setchannel = AdminJtcSetchannel(
        description=LocalizedString('admin.jtc.setchannel.description'),
        name=LocalizedString('admin.jtc.setchannel.name'),
        params=_n_admin_jtc_setchannel_params,
    )
    _n_admin_jtc = AdminJtc(
        removechannel=_n_admin_jtc_removechannel,
        setchannel=_n_admin_jtc_setchannel,
    )
    _n_admin_kick_params_reason = AdminKickParamsReason(
        description=LocalizedString('admin.kick.params.reason.description'),
        name=LocalizedString('admin.kick.params.reason.name'),
    )
    _n_admin_kick_params_user = AdminKickParamsUser(
        description=LocalizedString('admin.kick.params.user.description'),
        name=LocalizedString('admin.kick.params.user.name'),
    )
    _n_admin_kick_params = AdminKickParams(
        reason=_n_admin_kick_params_reason,
        user=_n_admin_kick_params_user,
    )
    _n_admin_kick = AdminKick(
        description=LocalizedString('admin.kick.description'),
        name=LocalizedString('admin.kick.name'),
        params=_n_admin_kick_params,
    )
    _n_admin_localegroup = AdminLocalegroup(
        description=LocalizedString('admin.localegroup.description'),
        name=LocalizedString('admin.localegroup.name'),
    )
    _n_admin_lock_params_channel = AdminLockParamsChannel(
        description=LocalizedString('admin.lock.params.channel.description'),
        name=LocalizedString('admin.lock.params.channel.name'),
    )
    _n_admin_lock_params = AdminLockParams(
        channel=_n_admin_lock_params_channel,
    )
    _n_admin_lock = AdminLock(
        description=LocalizedString('admin.lock.description'),
        name=LocalizedString('admin.lock.name'),
        params=_n_admin_lock_params,
    )
    _n_admin_messaging = AdminMessaging(
        description=LocalizedString('admin.messaging.description'),
        name=LocalizedString('admin.messaging.name'),
    )
    _n_admin_moderation = AdminModeration(
        description=LocalizedString('admin.moderation.description'),
        name=LocalizedString('admin.moderation.name'),
    )
    _n_admin_moverole_params_copymembers = AdminMoveroleParamsCopymembers(
        false=LocalizedString('admin.moverole.params.copymembers.false'),
        true=LocalizedString('admin.moverole.params.copymembers.true'),
    )
    _n_admin_moverole_params_position_above = AdminMoveroleParamsPositionAbove(
        description=LocalizedString('admin.moverole.params.position.above.description'),
        name=LocalizedString('admin.moverole.params.position.above.name'),
    )
    _n_admin_moverole_params_position_below = AdminMoveroleParamsPositionBelow(
        description=LocalizedString('admin.moverole.params.position.below.description'),
        name=LocalizedString('admin.moverole.params.position.below.name'),
    )
    _n_admin_moverole_params_position = AdminMoveroleParamsPosition(
        above=_n_admin_moverole_params_position_above,
        below=_n_admin_moverole_params_position_below,
        description=LocalizedString('admin.moverole.params.position.description'),
        name=LocalizedString('admin.moverole.params.position.name'),
    )
    _n_admin_moverole_params_role = AdminMoveroleParamsRole(
        description=LocalizedString('admin.moverole.params.role.description'),
        name=LocalizedString('admin.moverole.params.role.name'),
    )
    _n_admin_moverole_params_targetrole = AdminMoveroleParamsTargetrole(
        description=LocalizedString('admin.moverole.params.targetrole.description'),
        name=LocalizedString('admin.moverole.params.targetrole.name'),
    )
    _n_admin_moverole_params = AdminMoveroleParams(
        copymembers=_n_admin_moverole_params_copymembers,
        position=_n_admin_moverole_params_position,
        role=_n_admin_moverole_params_role,
        targetrole=_n_admin_moverole_params_targetrole,
    )
    _n_admin_moverole = AdminMoverole(
        description=LocalizedString('admin.moverole.description'),
        name=LocalizedString('admin.moverole.name'),
        params=_n_admin_moverole_params,
    )
    _n_admin_nickname_params_member = AdminNicknameParamsMember(
        description=LocalizedString('admin.nickname.params.member.description'),
        name=LocalizedString('admin.nickname.params.member.name'),
    )
    _n_admin_nickname_params_nickname = AdminNicknameParamsNickname(
        description=LocalizedString('admin.nickname.params.nickname.description'),
        name=LocalizedString('admin.nickname.params.nickname.name'),
    )
    _n_admin_nickname_params = AdminNicknameParams(
        member=_n_admin_nickname_params_member,
        nickname=_n_admin_nickname_params_nickname,
    )
    _n_admin_nickname = AdminNickname(
        description=LocalizedString('admin.nickname.description'),
        name=LocalizedString('admin.nickname.name'),
        params=_n_admin_nickname_params,
    )
    _n_admin_nuke_params_channel = AdminNukeParamsChannel(
        description=LocalizedString('admin.nuke.params.channel.description'),
        name=LocalizedString('admin.nuke.params.channel.name'),
    )
    _n_admin_nuke_params = AdminNukeParams(
        channel=_n_admin_nuke_params_channel,
    )
    _n_admin_nuke = AdminNuke(
        description=LocalizedString('admin.nuke.description'),
        name=LocalizedString('admin.nuke.name'),
        params=_n_admin_nuke_params,
    )
    _n_admin_purge_params_amount = AdminPurgeParamsAmount(
        description=LocalizedString('admin.purge.params.amount.description'),
        name=LocalizedString('admin.purge.params.amount.name'),
    )
    _n_admin_purge_params_channel = AdminPurgeParamsChannel(
        description=LocalizedString('admin.purge.params.channel.description'),
        name=LocalizedString('admin.purge.params.channel.name'),
    )
    _n_admin_purge_params_setting = AdminPurgeParamsSetting(
        all=LocalizedString('admin.purge.params.setting.all'),
        bot=LocalizedString('admin.purge.params.setting.bot'),
        botNotPinned=LocalizedString('admin.purge.params.setting.botNotPinned'),
        description=LocalizedString('admin.purge.params.setting.description'),
        embeds=LocalizedString('admin.purge.params.setting.embeds'),
        files=LocalizedString('admin.purge.params.setting.files'),
        notAdmin=LocalizedString('admin.purge.params.setting.notAdmin'),
        notAdminNotPinned=LocalizedString('admin.purge.params.setting.notAdminNotPinned'),
        notPinned=LocalizedString('admin.purge.params.setting.notPinned'),
        notUserAdmin=LocalizedString('admin.purge.params.setting.notUserAdmin'),
        user=LocalizedString('admin.purge.params.setting.user'),
        userNotPinned=LocalizedString('admin.purge.params.setting.userNotPinned'),
    )
    _n_admin_purge_params = AdminPurgeParams(
        amount=_n_admin_purge_params_amount,
        channel=_n_admin_purge_params_channel,
        setting=_n_admin_purge_params_setting,
    )
    _n_admin_purge = AdminPurge(
        description=LocalizedString('admin.purge.description'),
        name=LocalizedString('admin.purge.name'),
        params=_n_admin_purge_params,
    )
    _n_admin_purgegroup = AdminPurgegroup(
        description=LocalizedString('admin.purgegroup.description'),
        name=LocalizedString('admin.purgegroup.name'),
    )
    _n_admin_removerole_params_role = AdminRemoveroleParamsRole(
        description=LocalizedString('admin.removerole.params.role.description'),
        name=LocalizedString('admin.removerole.params.role.name'),
    )
    _n_admin_removerole_params_user = AdminRemoveroleParamsUser(
        description=LocalizedString('admin.removerole.params.user.description'),
        name=LocalizedString('admin.removerole.params.user.name'),
    )
    _n_admin_removerole_params = AdminRemoveroleParams(
        role=_n_admin_removerole_params_role,
        user=_n_admin_removerole_params_user,
    )
    _n_admin_removerole = AdminRemoverole(
        description=LocalizedString('admin.removerole.description'),
        name=LocalizedString('admin.removerole.name'),
        params=_n_admin_removerole_params,
    )
    _n_admin_removetimeout_params_member = AdminRemovetimeoutParamsMember(
        description=LocalizedString('admin.removetimeout.params.member.description'),
        name=LocalizedString('admin.removetimeout.params.member.name'),
    )
    _n_admin_removetimeout_params_reason = AdminRemovetimeoutParamsReason(
        description=LocalizedString('admin.removetimeout.params.reason.description'),
        name=LocalizedString('admin.removetimeout.params.reason.name'),
    )
    _n_admin_removetimeout_params = AdminRemovetimeoutParams(
        member=_n_admin_removetimeout_params_member,
        reason=_n_admin_removetimeout_params_reason,
    )
    _n_admin_removetimeout = AdminRemovetimeout(
        description=LocalizedString('admin.removetimeout.description'),
        name=LocalizedString('admin.removetimeout.name'),
        params=_n_admin_removetimeout_params,
    )
    _n_admin_report = AdminReport(
        description=LocalizedString('admin.report.description'),
        name=LocalizedString('admin.report.name'),
    )
    _n_admin_role = AdminRole(
        description=LocalizedString('admin.role.description'),
        name=LocalizedString('admin.role.name'),
    )
    _n_admin_rolemanage = AdminRolemanage(
        description=LocalizedString('admin.rolemanage.description'),
        name=LocalizedString('admin.rolemanage.name'),
    )
    _n_admin_rps_removechannel = AdminRpsRemovechannel(
        description=LocalizedString('admin.rps.removechannel.description'),
        name=LocalizedString('admin.rps.removechannel.name'),
    )
    _n_admin_rps_setchannel_params_channel = AdminRpsSetchannelParamsChannel(
        description=LocalizedString('admin.rps.setchannel.params.channel.description'),
        name=LocalizedString('admin.rps.setchannel.params.channel.name'),
    )
    _n_admin_rps_setchannel_params = AdminRpsSetchannelParams(
        channel=_n_admin_rps_setchannel_params_channel,
    )
    _n_admin_rps_setchannel = AdminRpsSetchannel(
        description=LocalizedString('admin.rps.setchannel.description'),
        name=LocalizedString('admin.rps.setchannel.name'),
        params=_n_admin_rps_setchannel_params,
    )
    _n_admin_rps_showreports_params_user = AdminRpsShowreportsParamsUser(
        description=LocalizedString('admin.rps.showreports.params.user.description'),
        name=LocalizedString('admin.rps.showreports.params.user.name'),
    )
    _n_admin_rps_showreports_params = AdminRpsShowreportsParams(
        user=_n_admin_rps_showreports_params_user,
    )
    _n_admin_rps_showreports = AdminRpsShowreports(
        description=LocalizedString('admin.rps.showreports.description'),
        name=LocalizedString('admin.rps.showreports.name'),
        params=_n_admin_rps_showreports_params,
    )
    _n_admin_rps_unblockreporter_params_user = AdminRpsUnblockreporterParamsUser(
        description=LocalizedString('admin.rps.unblockreporter.params.user.description'),
    )
    _n_admin_rps_unblockreporter_params = AdminRpsUnblockreporterParams(
        user=_n_admin_rps_unblockreporter_params_user,
    )
    _n_admin_rps_unblockreporter = AdminRpsUnblockreporter(
        description=LocalizedString('admin.rps.unblockreporter.description'),
        name=LocalizedString('admin.rps.unblockreporter.name'),
        params=_n_admin_rps_unblockreporter_params,
    )
    _n_admin_rps = AdminRps(
        removechannel=_n_admin_rps_removechannel,
        setchannel=_n_admin_rps_setchannel,
        showreports=_n_admin_rps_showreports,
        unblockreporter=_n_admin_rps_unblockreporter,
    )
    _n_admin_say_params_channel = AdminSayParamsChannel(
        description=LocalizedString('admin.say.params.channel.description'),
        name=LocalizedString('admin.say.params.channel.name'),
    )
    _n_admin_say_params_message = AdminSayParamsMessage(
        description=LocalizedString('admin.say.params.message.description'),
        name=LocalizedString('admin.say.params.message.name'),
    )
    _n_admin_say_params = AdminSayParams(
        channel=_n_admin_say_params_channel,
        message=_n_admin_say_params_message,
    )
    _n_admin_say = AdminSay(
        description=LocalizedString('admin.say.description'),
        name=LocalizedString('admin.say.name'),
        params=_n_admin_say_params,
    )
    _n_admin_setlocale_params_locale = AdminSetlocaleParamsLocale(
        description=LocalizedString('admin.setlocale.params.locale.description'),
        name=LocalizedString('admin.setlocale.params.locale.name'),
    )
    _n_admin_setlocale_params = AdminSetlocaleParams(
        locale=_n_admin_setlocale_params_locale,
    )
    _n_admin_setlocale = AdminSetlocale(
        description=LocalizedString('admin.setlocale.description'),
        name=LocalizedString('admin.setlocale.name'),
        params=_n_admin_setlocale_params,
    )
    _n_admin_setup = AdminSetup(
        description=LocalizedString('admin.setup.description'),
        name=LocalizedString('admin.setup.name'),
    )
    _n_admin_slowmode_params_channel = AdminSlowmodeParamsChannel(
        description=LocalizedString('admin.slowmode.params.channel.description'),
        name=LocalizedString('admin.slowmode.params.channel.name'),
    )
    _n_admin_slowmode_params_seconds = AdminSlowmodeParamsSeconds(
        description=LocalizedString('admin.slowmode.params.seconds.description'),
        name=LocalizedString('admin.slowmode.params.seconds.name'),
    )
    _n_admin_slowmode_params = AdminSlowmodeParams(
        channel=_n_admin_slowmode_params_channel,
        seconds=_n_admin_slowmode_params_seconds,
    )
    _n_admin_slowmode = AdminSlowmode(
        description=LocalizedString('admin.slowmode.description'),
        name=LocalizedString('admin.slowmode.name'),
        params=_n_admin_slowmode_params,
    )
    _n_admin_timeout_params_duration = AdminTimeoutParamsDuration(
        description=LocalizedString('admin.timeout.params.duration.description'),
        name=LocalizedString('admin.timeout.params.duration.name'),
    )
    _n_admin_timeout_params_member = AdminTimeoutParamsMember(
        description=LocalizedString('admin.timeout.params.member.description'),
        name=LocalizedString('admin.timeout.params.member.name'),
    )
    _n_admin_timeout_params_reason = AdminTimeoutParamsReason(
        description=LocalizedString('admin.timeout.params.reason.description'),
        name=LocalizedString('admin.timeout.params.reason.name'),
    )
    _n_admin_timeout_params = AdminTimeoutParams(
        duration=_n_admin_timeout_params_duration,
        member=_n_admin_timeout_params_member,
        reason=_n_admin_timeout_params_reason,
    )
    _n_admin_timeout = AdminTimeout(
        description=LocalizedString('admin.timeout.description'),
        name=LocalizedString('admin.timeout.name'),
        params=_n_admin_timeout_params,
    )
    _n_admin_tm_add_params_casesensitive = AdminTmAddParamsCasesensitive(
        description=LocalizedString('admin.tm.add.params.casesensitive.description'),
        false=LocalizedString('admin.tm.add.params.casesensitive.false'),
        name=LocalizedString('admin.tm.add.params.casesensitive.name'),
        true=LocalizedString('admin.tm.add.params.casesensitive.true'),
    )
    _n_admin_tm_add_params_response = AdminTmAddParamsResponse(
        description=LocalizedString('admin.tm.add.params.response.description'),
        name=LocalizedString('admin.tm.add.params.response.name'),
    )
    _n_admin_tm_add_params_trigger = AdminTmAddParamsTrigger(
        description=LocalizedString('admin.tm.add.params.trigger.description'),
        name=LocalizedString('admin.tm.add.params.trigger.name'),
    )
    _n_admin_tm_add_params = AdminTmAddParams(
        casesensitive=_n_admin_tm_add_params_casesensitive,
        response=_n_admin_tm_add_params_response,
        trigger=_n_admin_tm_add_params_trigger,
    )
    _n_admin_tm_add = AdminTmAdd(
        description=LocalizedString('admin.tm.add.description'),
        name=LocalizedString('admin.tm.add.name'),
        params=_n_admin_tm_add_params,
    )
    _n_admin_tm_configure = AdminTmConfigure(
        description=LocalizedString('admin.tm.configure.description'),
        name=LocalizedString('admin.tm.configure.name'),
    )
    _n_admin_tm = AdminTm(
        add=_n_admin_tm_add,
        configure=_n_admin_tm_configure,
    )
    _n_admin_triggermessages_params_message = AdminTriggermessagesParamsMessage(
        description=LocalizedString('admin.triggermessages.params.message.description'),
        name=LocalizedString('admin.triggermessages.params.message.name'),
    )
    _n_admin_triggermessages_params = AdminTriggermessagesParams(
        message=_n_admin_triggermessages_params_message,
    )
    _n_admin_triggermessages = AdminTriggermessages(
        description=LocalizedString('admin.triggermessages.description'),
        name=LocalizedString('admin.triggermessages.name'),
        params=_n_admin_triggermessages_params,
    )
    _n_admin_unban_params_reason = AdminUnbanParamsReason(
        description=LocalizedString('admin.unban.params.reason.description'),
        name=LocalizedString('admin.unban.params.reason.name'),
    )
    _n_admin_unban_params_username = AdminUnbanParamsUsername(
        description=LocalizedString('admin.unban.params.username.description'),
        name=LocalizedString('admin.unban.params.username.name'),
    )
    _n_admin_unban_params = AdminUnbanParams(
        reason=_n_admin_unban_params_reason,
        username=_n_admin_unban_params_username,
    )
    _n_admin_unban = AdminUnban(
        description=LocalizedString('admin.unban.description'),
        name=LocalizedString('admin.unban.name'),
        params=_n_admin_unban_params,
    )
    _n_admin_unlock_params_channel = AdminUnlockParamsChannel(
        description=LocalizedString('admin.unlock.params.channel.description'),
        name=LocalizedString('admin.unlock.params.channel.name'),
    )
    _n_admin_unlock_params = AdminUnlockParams(
        channel=_n_admin_unlock_params_channel,
    )
    _n_admin_unlock = AdminUnlock(
        description=LocalizedString('admin.unlock.description'),
        name=LocalizedString('admin.unlock.name'),
        params=_n_admin_unlock_params,
    )
    _n_admin_warn_add_params_member = AdminWarnAddParamsMember(
        description=LocalizedString('admin.warn.add.params.member.description'),
    )
    _n_admin_warn_add_params_reason = AdminWarnAddParamsReason(
        description=LocalizedString('admin.warn.add.params.reason.description'),
    )
    _n_admin_warn_add_params = AdminWarnAddParams(
        member=_n_admin_warn_add_params_member,
        reason=_n_admin_warn_add_params_reason,
    )
    _n_admin_warn_add = AdminWarnAdd(
        description=LocalizedString('admin.warn.add.description'),
        name=LocalizedString('admin.warn.add.name'),
        params=_n_admin_warn_add_params,
    )
    _n_admin_warn_config = AdminWarnConfig(
        description=LocalizedString('admin.warn.config.description'),
        name=LocalizedString('admin.warn.config.name'),
    )
    _n_admin_warn_view_params_member = AdminWarnViewParamsMember(
        description=LocalizedString('admin.warn.view.params.member.description'),
    )
    _n_admin_warn_view_params = AdminWarnViewParams(
        member=_n_admin_warn_view_params_member,
    )
    _n_admin_warn_view = AdminWarnView(
        description=LocalizedString('admin.warn.view.description'),
        name=LocalizedString('admin.warn.view.name'),
        params=_n_admin_warn_view_params,
    )
    _n_admin_warn = AdminWarn(
        add=_n_admin_warn_add,
        config=_n_admin_warn_config,
        description=LocalizedString('admin.warn.description'),
        name=LocalizedString('admin.warn.name'),
        view=_n_admin_warn_view,
    )
    _n_admin = Admin(
        addrole=_n_admin_addrole,
        ban=_n_admin_ban,
        boosterrole=_n_admin_boosterrole,
        channels=_n_admin_channels,
        copy7tv=_n_admin_copy7tv,
        copyemoji=_n_admin_copyemoji,
        copyrole=_n_admin_copyrole,
        createemoji=_n_admin_createemoji,
        createrole=_n_admin_createrole,
        createticket=_n_admin_createticket,
        deleterole=_n_admin_deleterole,
        description=LocalizedString('admin.description'),
        embed=_n_admin_embed,
        emoji=_n_admin_emoji,
        jointocreate=_n_admin_jointocreate,
        jtc=_n_admin_jtc,
        kick=_n_admin_kick,
        localegroup=_n_admin_localegroup,
        lock=_n_admin_lock,
        messaging=_n_admin_messaging,
        moderation=_n_admin_moderation,
        moverole=_n_admin_moverole,
        name=LocalizedString('admin.name'),
        nickname=_n_admin_nickname,
        nuke=_n_admin_nuke,
        purge=_n_admin_purge,
        purgegroup=_n_admin_purgegroup,
        removerole=_n_admin_removerole,
        removetimeout=_n_admin_removetimeout,
        report=_n_admin_report,
        role=_n_admin_role,
        rolemanage=_n_admin_rolemanage,
        rps=_n_admin_rps,
        say=_n_admin_say,
        setlocale=_n_admin_setlocale,
        setup=_n_admin_setup,
        slowmode=_n_admin_slowmode,
        timeout=_n_admin_timeout,
        tm=_n_admin_tm,
        triggermessages=_n_admin_triggermessages,
        unban=_n_admin_unban,
        unlock=_n_admin_unlock,
        warn=_n_admin_warn,
    )
    return _n_admin


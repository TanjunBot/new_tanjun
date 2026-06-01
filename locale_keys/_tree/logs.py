"""Auto-generated locale tree: logs. Do not edit."""
from __future__ import annotations

from dataclasses import dataclass

from locale_keys.types import LocalizedString, ResolveMap


@dataclass(frozen=True, slots=True)
class Logs:
    description: LocalizedString
    name: LocalizedString
    automodAction: LogsAutomodAction
    automodRuleCreate: LogsAutomodRuleCreate
    automodRuleDelete: LogsAutomodRuleDelete
    automodRuleUpdate: LogsAutomodRuleUpdate
    blacklist: LogsBlacklist
    blacklistc: LogsBlacklistc
    blacklistcat: LogsBlacklistcat
    blacklistr: LogsBlacklistr
    blacklistu: LogsBlacklistu
    blacklistv: LogsBlacklistv
    configure: LogsConfigure
    guildChannelCreate: LogsGuildChannelCreate
    guildChannelDelete: LogsGuildChannelDelete
    guildChannelUpdate: LogsGuildChannelUpdate
    guildRoleCreate: LogsGuildRoleCreate
    guildRoleDelete: LogsGuildRoleDelete
    guildRoleUpdate: LogsGuildRoleUpdate
    guildUpdate: LogsGuildUpdate
    guild_channelCreate: LogsGuild_channelCreate
    guild_channelDelete: LogsGuild_channelDelete
    guild_channelUpdate: LogsGuild_channelUpdate
    inviteCreate: LogsInviteCreate
    inviteDelete: LogsInviteDelete
    memberBan: LogsMemberBan
    memberJoin: LogsMemberJoin
    memberRemove: LogsMemberRemove
    memberUnban: LogsMemberUnban
    memberUpdate: LogsMemberUpdate
    messageDelete: LogsMessageDelete
    messageEdit: LogsMessageEdit
    permissions: LogsPermissions
    presenceUpdate: LogsPresenceUpdate
    reactionAdd: LogsReactionAdd
    reactionRemove: LogsReactionRemove
    remove: LogsRemove
    set: LogsSet
    userUpdate: LogsUserUpdate

@dataclass(frozen=True, slots=True)
class LogsAutomodRuleCreate:
    actions: LocalizedString
    allow_list: LocalizedString
    block_member_interaction: LocalizedString
    block_message: LocalizedString
    created_by: LocalizedString
    enabled: LocalizedString
    excluded_channels: LocalizedString
    excluded_roles: LocalizedString
    keywordFilters: LocalizedString
    max_mentions: LocalizedString
    mentionSpamProtection: LocalizedString
    name: LocalizedString
    presets: LocalizedString
    regexPatterns: LocalizedString
    send_warning_message: LocalizedString
    timeout: LocalizedString
    title: LocalizedString
    trigger: LocalizedString
    triggerType: LocalizedString
    AutoModRuleTriggerType: LogsAutomodRuleCreateAutoModRuleTriggerType
    timeout_duration: LogsAutomodRuleCreateTimeout_duration
    resolve: ResolveMap

@dataclass(frozen=True, slots=True)
class LogsBlacklistc:
    description: LocalizedString
    name: LocalizedString
    add: LogsBlacklistcAdd
    remove: LogsBlacklistcRemove
    show: LogsBlacklistcShow

@dataclass(frozen=True, slots=True)
class LogsBlacklistr:
    description: LocalizedString
    name: LocalizedString
    add: LogsBlacklistrAdd
    remove: LogsBlacklistrRemove
    show: LogsBlacklistrShow

@dataclass(frozen=True, slots=True)
class LogsBlacklistu:
    description: LocalizedString
    name: LocalizedString
    add: LogsBlacklistuAdd
    remove: LogsBlacklistuRemove
    show: LogsBlacklistuShow

@dataclass(frozen=True, slots=True)
class LogsGuildChannelCreate:
    category: LocalizedString
    created_at: LocalizedString
    created_by: LocalizedString
    name: LocalizedString
    permissionOverwriteAllowed: LocalizedString
    permissionOverwriteDenied: LocalizedString
    permissionOverwriteNeutral: LocalizedString
    permissionOverwriteTarget: LocalizedString
    permissionOverwrites: LocalizedString
    title: LocalizedString
    topic: LocalizedString
    type: LocalizedString
    types: LogsGuildChannelCreateTypes

@dataclass(frozen=True, slots=True)
class LogsGuildChannelDelete:
    category: LocalizedString
    created_at: LocalizedString
    deleted_by: LocalizedString
    name: LocalizedString
    permissionOverwriteAllowed: LocalizedString
    permissionOverwriteDenied: LocalizedString
    permissionOverwriteNeutral: LocalizedString
    permissionOverwriteTarget: LocalizedString
    permissionOverwrites: LocalizedString
    title: LocalizedString
    topic: LocalizedString
    type: LocalizedString
    types: LogsGuildChannelDeleteTypes

@dataclass(frozen=True, slots=True)
class LogsGuildUpdate:
    addedEmojis: LocalizedString
    addedFeatures: LocalizedString
    afkChannel: LocalizedString
    afkTimeout: LocalizedString
    banner: LocalizedString
    defaultNotifications: LocalizedString
    description: LocalizedString
    discoverySplash: LocalizedString
    emojiLimit: LocalizedString
    explicitContentFilter: LocalizedString
    filesizeLimit: LocalizedString
    icon: LocalizedString
    invitesPausedUntil: LocalizedString
    maxMembers: LocalizedString
    maxPresences: LocalizedString
    maxVideoChannelUsers: LocalizedString
    name: LocalizedString
    none: LocalizedString
    nsfwLevel: LocalizedString
    owner: LocalizedString
    preferredLocale: LocalizedString
    premiumSubscriberRole: LocalizedString
    premiumSubscribers: LocalizedString
    premiumTier: LocalizedString
    publicUpdatesChannel: LocalizedString
    removedEmojis: LocalizedString
    removedFeatures: LocalizedString
    rulesChannel: LocalizedString
    safetyAlertsChannel: LocalizedString
    title: LocalizedString
    verificationLevel: LocalizedString
    defaultNotificationsLocales: LogsGuildUpdateDefaultNotificationsLocales
    discoverySplashLocales: LogsGuildUpdateDiscoverySplashLocales
    explicitContentFilterLocales: LogsGuildUpdateExplicitContentFilterLocales
    featuresLocales: LogsGuildUpdateFeaturesLocales
    iconLocales: LogsGuildUpdateIconLocales
    invitesPausedUntilLocales: LogsGuildUpdateInvitesPausedUntilLocales
    nsfwLevelLocales: LogsGuildUpdateNsfwLevelLocales
    preferredLocaleLocales: LogsGuildUpdatePreferredLocaleLocales
    premiumProgressBarEnabled: LogsGuildUpdatePremiumProgressBarEnabled
    premiumProgressBarLocales: LogsGuildUpdatePremiumProgressBarLocales
    unavailableLocales: LogsGuildUpdateUnavailableLocales
    verificationLevelLocales: LogsGuildUpdateVerificationLevelLocales

@dataclass(frozen=True, slots=True)
class LogsInviteCreate:
    channel: LocalizedString
    createdBy: LocalizedString
    expires: LocalizedString
    invite: LocalizedString
    max_uses: LocalizedString
    scheduledEvent: LocalizedString
    targetApplication: LocalizedString
    targetUser: LocalizedString
    temporary: LocalizedString
    title: LocalizedString
    expiresLocales: LogsInviteCreateExpiresLocales
    maxUsesLocales: LogsInviteCreateMaxUsesLocales
    targetTypeLocales: LogsInviteCreateTargetTypeLocales

@dataclass(frozen=True, slots=True)
class LogsMemberUpdate:
    addedRoles: LocalizedString
    banner: LocalizedString
    displayName: LocalizedString
    guildAvatar: LocalizedString
    name: LocalizedString
    pending: LocalizedString
    pendingRemoved: LocalizedString
    removedRoles: LocalizedString
    timeout: LocalizedString
    timeoutRemoved: LocalizedString
    title: LocalizedString
    guildAvatarLocales: LogsMemberUpdateGuildAvatarLocales

@dataclass(frozen=True, slots=True)
class LogsPermissions:
    add_reaction: LocalizedString
    add_reactions: LocalizedString
    administrator: LocalizedString
    attach_files: LocalizedString
    ban_members: LocalizedString
    change_nickname: LocalizedString
    connect: LocalizedString
    create_events: LocalizedString
    create_expressions: LocalizedString
    create_instant_invite: LocalizedString
    create_polls: LocalizedString
    create_private_threads: LocalizedString
    create_public_threads: LocalizedString
    deafen_members: LocalizedString
    embed_links: LocalizedString
    external_emojis: LocalizedString
    external_stickers: LocalizedString
    kick_members: LocalizedString
    manage_channels: LocalizedString
    manage_emojis: LocalizedString
    manage_emojis_and_stickers: LocalizedString
    manage_events: LocalizedString
    manage_expressions: LocalizedString
    manage_guild: LocalizedString
    manage_messages: LocalizedString
    manage_nicknames: LocalizedString
    manage_permissions: LocalizedString
    manage_roles: LocalizedString
    manage_stickers: LocalizedString
    manage_threads: LocalizedString
    manage_webhooks: LocalizedString
    mention_everyone: LocalizedString
    moderate_members: LocalizedString
    move_members: LocalizedString
    mute_members: LocalizedString
    priority_speaker: LocalizedString
    read_message_history: LocalizedString
    read_messages: LocalizedString
    request_to_speak: LocalizedString
    send_messages: LocalizedString
    send_messages_in_threads: LocalizedString
    send_polls: LocalizedString
    send_tts_messages: LocalizedString
    send_voice_messages: LocalizedString
    speak: LocalizedString
    stream: LocalizedString
    use_application_commands: LocalizedString
    use_embedded_activities: LocalizedString
    use_external_apps: LocalizedString
    use_external_emojis: LocalizedString
    use_external_sounds: LocalizedString
    use_external_stickers: LocalizedString
    use_soundboard: LocalizedString
    use_voice_activation: LocalizedString
    view_audit_log: LocalizedString
    view_channel: LocalizedString
    view_creator_monetization_analytics: LocalizedString
    view_guild_insights: LocalizedString
    resolve: ResolveMap

@dataclass(frozen=True, slots=True)
class LogsSet:
    description: LocalizedString
    name: LocalizedString
    params: LogsSetParams

@dataclass(frozen=True, slots=True)
class LogsUserUpdate:
    avatar: LocalizedString
    banner: LocalizedString
    globalName: LocalizedString
    name: LocalizedString
    title: LocalizedString
    userName: LocalizedString
    guildAvatarLocales: LogsUserUpdateGuildAvatarLocales

@dataclass(frozen=True, slots=True)
class LogsBlacklistcat:
    description: LocalizedString
    name: LocalizedString
    add: LogsBlacklistcatAdd
    remove: LogsBlacklistcatRemove
    show: LogsBlacklistcatShow

@dataclass(frozen=True, slots=True)
class LogsBlacklistv:
    description: LocalizedString
    name: LocalizedString
    add: LogsBlacklistvAdd
    remove: LogsBlacklistvRemove
    show: LogsBlacklistvShow

@dataclass(frozen=True, slots=True)
class LogsAutomodAction:
    action: LocalizedString
    actionWasTaken: LocalizedString
    message: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsAutomodRuleDelete:
    deleted_by: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsAutomodRuleUpdate:
    footer: LocalizedString
    title: LocalizedString
    updated_by: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklist:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsConfigure:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildChannelUpdate:
    category: LocalizedString
    defaultAutoArchiveDuration: LocalizedString
    defaultThreadAutoArchiveDuration: LocalizedString
    mention: LocalizedString
    name: LocalizedString
    no: LocalizedString
    nsfw: LocalizedString
    permissionOverwriteAddedAllow: LocalizedString
    permissionOverwriteAddedDeny: LocalizedString
    permissionOverwriteAddedNeutral: LocalizedString
    permissionOverwriteAllowed: LocalizedString
    permissionOverwriteDenied: LocalizedString
    permissionOverwriteModified: LocalizedString
    permissionOverwriteNeutral: LocalizedString
    permissionOverwriteNew: LocalizedString
    permissionOverwriteRemovedAllow: LocalizedString
    permissionOverwriteRemovedDeny: LocalizedString
    permissionOverwriteRemovedNeutral: LocalizedString
    permissionOverwriteTarget: LocalizedString
    permissionOverwrites: LocalizedString
    slowmodeDelay: LocalizedString
    title: LocalizedString
    topic: LocalizedString
    type: LocalizedString
    updated_by: LocalizedString
    yes: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildRoleCreate:
    color: LocalizedString
    createdBy: LocalizedString
    displayIcon: LocalizedString
    hoist: LocalizedString
    managed: LocalizedString
    mentionable: LocalizedString
    name: LocalizedString
    permissions: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildRoleDelete:
    deletedBy: LocalizedString
    name: LocalizedString
    permissions: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildRoleUpdate:
    addedPermissions: LocalizedString
    color: LocalizedString
    displayIcon: LocalizedString
    hoistNoLonger: LocalizedString
    hoistNow: LocalizedString
    icon: LocalizedString
    managedNoLonger: LocalizedString
    managedNow: LocalizedString
    mentionableNoLonger: LocalizedString
    mentionableNow: LocalizedString
    name: LocalizedString
    removedPermissions: LocalizedString
    title: LocalizedString
    updatedBy: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuild_channelCreate:
    category: LocalizedString
    created_at: LocalizedString
    created_by: LocalizedString
    name: LocalizedString
    permissionOverwrites: LocalizedString
    title: LocalizedString
    topic: LocalizedString
    type: LocalizedString
    types: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuild_channelDelete:
    category: LocalizedString
    created_at: LocalizedString
    deleted_by: LocalizedString
    name: LocalizedString
    permissionOverwriteAllowed: LocalizedString
    permissionOverwriteDenied: LocalizedString
    permissionOverwriteTarget: LocalizedString
    permissionOverwrites: LocalizedString
    title: LocalizedString
    topic: LocalizedString
    type: LocalizedString
    types: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuild_channelUpdate:
    category: LocalizedString
    defaultAutoArchiveDuration: LocalizedString
    defaultThreadAutoArchiveDuration: LocalizedString
    mention: LocalizedString
    name: LocalizedString
    no: LocalizedString
    nsfw: LocalizedString
    permissionOverwriteAddedAllow: LocalizedString
    permissionOverwriteAddedDeny: LocalizedString
    permissionOverwriteAddedNeutral: LocalizedString
    permissionOverwriteAllowed: LocalizedString
    permissionOverwriteDenied: LocalizedString
    permissionOverwriteModified: LocalizedString
    permissionOverwriteNeutral: LocalizedString
    permissionOverwriteNew: LocalizedString
    permissionOverwriteRemoved: LocalizedString
    permissionOverwriteRemovedAllow: LocalizedString
    permissionOverwriteRemovedDeny: LocalizedString
    permissionOverwriteRemovedNeutral: LocalizedString
    slowmodeDelay: LocalizedString
    title: LocalizedString
    topic: LocalizedString
    type: LocalizedString
    types: LocalizedString
    updated_by: LocalizedString
    yes: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsInviteDelete:
    invite: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsMemberBan:
    banned_by: LocalizedString
    name: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsMemberJoin:
    name: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsMemberRemove:
    name: LocalizedString
    roles: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsMemberUnban:
    name: LocalizedString
    title: LocalizedString
    unbanned_by: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsMessageDelete:
    attachments: LocalizedString
    content: LocalizedString
    deletedBy: LocalizedString
    embeds: LocalizedString
    name: LocalizedString
    title: LocalizedString
    urlNotAvaiableLocale: LocalizedString
    url_not_available_locale: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsMessageEdit:
    addedAttachments: LocalizedString
    content: LocalizedString
    diff: LocalizedString
    ellipsis: LocalizedString
    embeds: LocalizedString
    name: LocalizedString
    removedAttachments: LocalizedString
    title: LocalizedString
    tooLongNotice: LocalizedString
    truncatedNotice: LocalizedString
    urlNotAvaiableLocale: LocalizedString
    url_not_available_locale: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsPresenceUpdate:
    activity: LocalizedString
    name: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsReactionAdd:
    name: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsReactionRemove:
    name: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsRemove:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsAutomodRuleCreateAutoModRuleTriggerType:
    harmful_link: LocalizedString
    keyword: LocalizedString
    keyword_preset: LocalizedString
    member_profile: LocalizedString
    mention_spam: LocalizedString
    spam: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsAutomodRuleCreateTimeout_duration:
    _0_01_00: LocalizedString
    _0_05_00: LocalizedString
    _0_10_00: LocalizedString
    _1_day__0_00_00: LocalizedString
    _1_00_00: LocalizedString
    _7_days__0_00_00: LocalizedString
    resolve: ResolveMap

@dataclass(frozen=True, slots=True)
class LogsBlacklistcAdd:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistcAddParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistcRemove:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistcRemoveParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistcShow:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistrAdd:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistrAddParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistrRemove:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistrRemoveParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistrShow:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistuAdd:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistuAddParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistuRemove:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistuRemoveParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistuShow:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildChannelCreateTypes:
    category: LocalizedString
    forum: LocalizedString
    news: LocalizedString
    stage: LocalizedString
    text: LocalizedString
    voice: LocalizedString
    resolve: ResolveMap

@dataclass(frozen=True, slots=True)
class LogsGuildChannelDeleteTypes:
    category: LocalizedString
    forum: LocalizedString
    stage: LocalizedString
    text: LocalizedString
    voice: LocalizedString
    resolve: ResolveMap

@dataclass(frozen=True, slots=True)
class LogsGuildUpdateDefaultNotificationsLocales:
    allMembers: LocalizedString
    all_members: LocalizedString
    onlyMentions: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildUpdateDiscoverySplashLocales:
    url: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildUpdateExplicitContentFilterLocales:
    allMembers: LocalizedString
    all_members: LocalizedString
    disabled: LocalizedString
    noRole: LocalizedString
    no_role: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildUpdateFeaturesLocales:
    ANIMATED_BANNER: LocalizedString
    ANIMATED_ICON: LocalizedString
    APPLICATION_COMMAND_PERMISSIONS_V2: LocalizedString
    AUTO_MODERATION: LocalizedString
    BANNER: LocalizedString
    COMMUNITY: LocalizedString
    CREATOR_MONETIZATION_ANALYTICS: LocalizedString
    CREATOR_STORE_PAGE: LocalizedString
    DEVELOPER_SUPPORT_SERVER: LocalizedString
    DISCOVERABLE: LocalizedString
    FEATURABLE: LocalizedString
    INVITES_DISABLED: LocalizedString
    INVITE_SPLASH: LocalizedString
    MEMBER_VERIFICATION_GATE_ENABLED: LocalizedString
    MORE_SOUNDBOARD: LocalizedString
    MORE_STICKERS: LocalizedString
    NEWS: LocalizedString
    PARTNERED: LocalizedString
    PREVIEW_ENABLED: LocalizedString
    RAID_ALERTS_DISABLED: LocalizedString
    ROLE_ICONS: LocalizedString
    ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE: LocalizedString
    ROLE_SUBSCRIPTIONS_ENABLED: LocalizedString
    SOUNDBOARD: LocalizedString
    TICKETED_EVENTS_ENABLED: LocalizedString
    VANITY_URL: LocalizedString
    VERIFIED: LocalizedString
    VIP_REGIONS: LocalizedString
    WELCOME_SCREEN_ENABLED: LocalizedString
    resolve: ResolveMap

@dataclass(frozen=True, slots=True)
class LogsGuildUpdateIconLocales:
    noIcon: LocalizedString
    url: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildUpdateInvitesPausedUntilLocales:
    notPaused: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildUpdateNsfwLevelLocales:
    ageRegistered: LocalizedString
    default: LocalizedString
    explicit: LocalizedString
    safe: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildUpdatePreferredLocaleLocales:
    bg: LocalizedString
    cs: LocalizedString
    da: LocalizedString
    de: LocalizedString
    el: LocalizedString
    en_GB: LocalizedString
    en_US: LocalizedString
    es_419: LocalizedString
    es_ES: LocalizedString
    fi: LocalizedString
    fr: LocalizedString
    hi: LocalizedString
    hr: LocalizedString
    hu: LocalizedString
    id: LocalizedString
    it: LocalizedString
    ko: LocalizedString
    lt: LocalizedString
    nl: LocalizedString
    no: LocalizedString
    pl: LocalizedString
    pt_BR: LocalizedString
    ro: LocalizedString
    sv_SE: LocalizedString
    th: LocalizedString
    tr: LocalizedString
    uk: LocalizedString
    vi: LocalizedString
    zh_CN: LocalizedString
    zh_TW: LocalizedString
    resolve: ResolveMap

@dataclass(frozen=True, slots=True)
class LogsGuildUpdatePremiumProgressBarEnabled:
    activated: LocalizedString
    deactivated: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildUpdatePremiumProgressBarLocales:
    activated: LocalizedString
    deactivated: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildUpdateUnavailableLocales:
    available: LocalizedString
    unavailable: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsGuildUpdateVerificationLevelLocales:
    high: LocalizedString
    highest: LocalizedString
    low: LocalizedString
    medium: LocalizedString
    none: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsInviteCreateExpiresLocales:
    never: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsInviteCreateMaxUsesLocales:
    infinite: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsInviteCreateTargetTypeLocales:
    InviteTarget_embeddedApplication: LocalizedString
    InviteTarget_stream: LocalizedString
    InviteTarget_unknown: LocalizedString
    resolve: ResolveMap

@dataclass(frozen=True, slots=True)
class LogsMemberUpdateGuildAvatarLocales:
    none: LocalizedString
    url: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsSetParams:
    channel: LogsSetParamsChannel

@dataclass(frozen=True, slots=True)
class LogsUserUpdateGuildAvatarLocales:
    none: LocalizedString
    url: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistcatAdd:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistcatAddParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistcatRemove:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistcatRemoveParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistcatShow:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistvAdd:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistvAddParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistvRemove:
    description: LocalizedString
    name: LocalizedString
    params: LogsBlacklistvRemoveParams

@dataclass(frozen=True, slots=True)
class LogsBlacklistvShow:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistcAddParams:
    channel: LogsBlacklistcAddParamsChannel

@dataclass(frozen=True, slots=True)
class LogsBlacklistcRemoveParams:
    channel: LogsBlacklistcRemoveParamsChannel

@dataclass(frozen=True, slots=True)
class LogsBlacklistrAddParams:
    role: LogsBlacklistrAddParamsRole

@dataclass(frozen=True, slots=True)
class LogsBlacklistrRemoveParams:
    role: LogsBlacklistrRemoveParamsRole

@dataclass(frozen=True, slots=True)
class LogsBlacklistuAddParams:
    user: LogsBlacklistuAddParamsUser

@dataclass(frozen=True, slots=True)
class LogsBlacklistuRemoveParams:
    user: LogsBlacklistuRemoveParamsUser

@dataclass(frozen=True, slots=True)
class LogsSetParamsChannel:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistcatAddParams:
    channel: LogsBlacklistcatAddParamsChannel

@dataclass(frozen=True, slots=True)
class LogsBlacklistcatRemoveParams:
    channel: LogsBlacklistcatRemoveParamsChannel

@dataclass(frozen=True, slots=True)
class LogsBlacklistvAddParams:
    channel: LogsBlacklistvAddParamsChannel

@dataclass(frozen=True, slots=True)
class LogsBlacklistvRemoveParams:
    channel: LogsBlacklistvRemoveParamsChannel

@dataclass(frozen=True, slots=True)
class LogsBlacklistcAddParamsChannel:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistcRemoveParamsChannel:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistrAddParamsRole:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistrRemoveParamsRole:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistuAddParamsUser:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistuRemoveParamsUser:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistcatAddParamsChannel:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistcatRemoveParamsChannel:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistvAddParamsChannel:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class LogsBlacklistvRemoveParamsChannel:
    description: LocalizedString

def build_logs() -> Logs:
    _n_logs_automodAction = LogsAutomodAction(
        action=LocalizedString('logs.automodAction.action'),
        actionWasTaken=LocalizedString('logs.automodAction.actionWasTaken'),
        message=LocalizedString('logs.automodAction.message'),
        title=LocalizedString('logs.automodAction.title'),
    )
    _n_logs_automodRuleCreate_AutoModRuleTriggerType = LogsAutomodRuleCreateAutoModRuleTriggerType(
        harmful_link=LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.harmful_link'),
        keyword=LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.keyword'),
        keyword_preset=LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.keyword_preset'),
        member_profile=LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.member_profile'),
        mention_spam=LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.mention_spam'),
        spam=LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.spam'),
    )
    _n_logs_automodRuleCreate_timeout_duration_resolve = ResolveMap(
        'logs.automodRuleCreate.timeout_duration.',
        {
            '0:01:00': LocalizedString('logs.automodRuleCreate.timeout_duration.0:01:00'),
            '0:05:00': LocalizedString('logs.automodRuleCreate.timeout_duration.0:05:00'),
            '0:10:00': LocalizedString('logs.automodRuleCreate.timeout_duration.0:10:00'),
            '1 day, 0:00:00': LocalizedString('logs.automodRuleCreate.timeout_duration.1 day, 0:00:00'),
            '1:00:00': LocalizedString('logs.automodRuleCreate.timeout_duration.1:00:00'),
            '7 days, 0:00:00': LocalizedString('logs.automodRuleCreate.timeout_duration.7 days, 0:00:00'),
        },
    )
    _n_logs_automodRuleCreate_timeout_duration = LogsAutomodRuleCreateTimeout_duration(
        _0_01_00=LocalizedString('logs.automodRuleCreate.timeout_duration.0:01:00'),
        _0_05_00=LocalizedString('logs.automodRuleCreate.timeout_duration.0:05:00'),
        _0_10_00=LocalizedString('logs.automodRuleCreate.timeout_duration.0:10:00'),
        _1_00_00=LocalizedString('logs.automodRuleCreate.timeout_duration.1:00:00'),
        _1_day__0_00_00=LocalizedString('logs.automodRuleCreate.timeout_duration.1 day, 0:00:00'),
        _7_days__0_00_00=LocalizedString('logs.automodRuleCreate.timeout_duration.7 days, 0:00:00'),
        resolve=_n_logs_automodRuleCreate_timeout_duration_resolve,
    )
    _n_logs_automodRuleCreate_resolve = ResolveMap(
        'logs.automodRuleCreate.',
        {
            'AutoModRuleTriggerType.harmful_link': LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.harmful_link'),
            'AutoModRuleTriggerType.keyword': LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.keyword'),
            'AutoModRuleTriggerType.keyword_preset': LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.keyword_preset'),
            'AutoModRuleTriggerType.member_profile': LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.member_profile'),
            'AutoModRuleTriggerType.mention_spam': LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.mention_spam'),
            'AutoModRuleTriggerType.spam': LocalizedString('logs.automodRuleCreate.AutoModRuleTriggerType.spam'),
            'actions': LocalizedString('logs.automodRuleCreate.actions'),
            'allow_list': LocalizedString('logs.automodRuleCreate.allow_list'),
            'block_member_interaction': LocalizedString('logs.automodRuleCreate.block_member_interaction'),
            'block_message': LocalizedString('logs.automodRuleCreate.block_message'),
            'created_by': LocalizedString('logs.automodRuleCreate.created_by'),
            'enabled': LocalizedString('logs.automodRuleCreate.enabled'),
            'excluded_channels': LocalizedString('logs.automodRuleCreate.excluded_channels'),
            'excluded_roles': LocalizedString('logs.automodRuleCreate.excluded_roles'),
            'keywordFilters': LocalizedString('logs.automodRuleCreate.keywordFilters'),
            'max_mentions': LocalizedString('logs.automodRuleCreate.max_mentions'),
            'mentionSpamProtection': LocalizedString('logs.automodRuleCreate.mentionSpamProtection'),
            'name': LocalizedString('logs.automodRuleCreate.name'),
            'presets': LocalizedString('logs.automodRuleCreate.presets'),
            'regexPatterns': LocalizedString('logs.automodRuleCreate.regexPatterns'),
            'send_warning_message': LocalizedString('logs.automodRuleCreate.send_warning_message'),
            'timeout': LocalizedString('logs.automodRuleCreate.timeout'),
            'timeout_duration.0:01:00': LocalizedString('logs.automodRuleCreate.timeout_duration.0:01:00'),
            'timeout_duration.0:05:00': LocalizedString('logs.automodRuleCreate.timeout_duration.0:05:00'),
            'timeout_duration.0:10:00': LocalizedString('logs.automodRuleCreate.timeout_duration.0:10:00'),
            'timeout_duration.1 day, 0:00:00': LocalizedString('logs.automodRuleCreate.timeout_duration.1 day, 0:00:00'),
            'timeout_duration.1:00:00': LocalizedString('logs.automodRuleCreate.timeout_duration.1:00:00'),
            'timeout_duration.7 days, 0:00:00': LocalizedString('logs.automodRuleCreate.timeout_duration.7 days, 0:00:00'),
            'title': LocalizedString('logs.automodRuleCreate.title'),
            'trigger': LocalizedString('logs.automodRuleCreate.trigger'),
            'triggerType': LocalizedString('logs.automodRuleCreate.triggerType'),
        },
    )
    _n_logs_automodRuleCreate = LogsAutomodRuleCreate(
        AutoModRuleTriggerType=_n_logs_automodRuleCreate_AutoModRuleTriggerType,
        actions=LocalizedString('logs.automodRuleCreate.actions'),
        allow_list=LocalizedString('logs.automodRuleCreate.allow_list'),
        block_member_interaction=LocalizedString('logs.automodRuleCreate.block_member_interaction'),
        block_message=LocalizedString('logs.automodRuleCreate.block_message'),
        created_by=LocalizedString('logs.automodRuleCreate.created_by'),
        enabled=LocalizedString('logs.automodRuleCreate.enabled'),
        excluded_channels=LocalizedString('logs.automodRuleCreate.excluded_channels'),
        excluded_roles=LocalizedString('logs.automodRuleCreate.excluded_roles'),
        keywordFilters=LocalizedString('logs.automodRuleCreate.keywordFilters'),
        max_mentions=LocalizedString('logs.automodRuleCreate.max_mentions'),
        mentionSpamProtection=LocalizedString('logs.automodRuleCreate.mentionSpamProtection'),
        name=LocalizedString('logs.automodRuleCreate.name'),
        presets=LocalizedString('logs.automodRuleCreate.presets'),
        regexPatterns=LocalizedString('logs.automodRuleCreate.regexPatterns'),
        resolve=_n_logs_automodRuleCreate_resolve,
        send_warning_message=LocalizedString('logs.automodRuleCreate.send_warning_message'),
        timeout=LocalizedString('logs.automodRuleCreate.timeout'),
        timeout_duration=_n_logs_automodRuleCreate_timeout_duration,
        title=LocalizedString('logs.automodRuleCreate.title'),
        trigger=LocalizedString('logs.automodRuleCreate.trigger'),
        triggerType=LocalizedString('logs.automodRuleCreate.triggerType'),
    )
    _n_logs_automodRuleDelete = LogsAutomodRuleDelete(
        deleted_by=LocalizedString('logs.automodRuleDelete.deleted_by'),
        title=LocalizedString('logs.automodRuleDelete.title'),
    )
    _n_logs_automodRuleUpdate = LogsAutomodRuleUpdate(
        footer=LocalizedString('logs.automodRuleUpdate.footer'),
        title=LocalizedString('logs.automodRuleUpdate.title'),
        updated_by=LocalizedString('logs.automodRuleUpdate.updated_by'),
    )
    _n_logs_blacklist = LogsBlacklist(
        description=LocalizedString('logs.blacklist.description'),
        name=LocalizedString('logs.blacklist.name'),
    )
    _n_logs_blacklistc_add_params_channel = LogsBlacklistcAddParamsChannel(
        description=LocalizedString('logs.blacklistc.add.params.channel.description'),
    )
    _n_logs_blacklistc_add_params = LogsBlacklistcAddParams(
        channel=_n_logs_blacklistc_add_params_channel,
    )
    _n_logs_blacklistc_add = LogsBlacklistcAdd(
        description=LocalizedString('logs.blacklistc.add.description'),
        name=LocalizedString('logs.blacklistc.add.name'),
        params=_n_logs_blacklistc_add_params,
    )
    _n_logs_blacklistc_remove_params_channel = LogsBlacklistcRemoveParamsChannel(
        description=LocalizedString('logs.blacklistc.remove.params.channel.description'),
    )
    _n_logs_blacklistc_remove_params = LogsBlacklistcRemoveParams(
        channel=_n_logs_blacklistc_remove_params_channel,
    )
    _n_logs_blacklistc_remove = LogsBlacklistcRemove(
        description=LocalizedString('logs.blacklistc.remove.description'),
        name=LocalizedString('logs.blacklistc.remove.name'),
        params=_n_logs_blacklistc_remove_params,
    )
    _n_logs_blacklistc_show = LogsBlacklistcShow(
        description=LocalizedString('logs.blacklistc.show.description'),
        name=LocalizedString('logs.blacklistc.show.name'),
    )
    _n_logs_blacklistc = LogsBlacklistc(
        add=_n_logs_blacklistc_add,
        description=LocalizedString('logs.blacklistc.description'),
        name=LocalizedString('logs.blacklistc.name'),
        remove=_n_logs_blacklistc_remove,
        show=_n_logs_blacklistc_show,
    )
    _n_logs_blacklistcat_add_params_channel = LogsBlacklistcatAddParamsChannel(
        description=LocalizedString('logs.blacklistcat.add.params.channel.description'),
    )
    _n_logs_blacklistcat_add_params = LogsBlacklistcatAddParams(
        channel=_n_logs_blacklistcat_add_params_channel,
    )
    _n_logs_blacklistcat_add = LogsBlacklistcatAdd(
        description=LocalizedString('logs.blacklistcat.add.description'),
        name=LocalizedString('logs.blacklistcat.add.name'),
        params=_n_logs_blacklistcat_add_params,
    )
    _n_logs_blacklistcat_remove_params_channel = LogsBlacklistcatRemoveParamsChannel(
        description=LocalizedString('logs.blacklistcat.remove.params.channel.description'),
    )
    _n_logs_blacklistcat_remove_params = LogsBlacklistcatRemoveParams(
        channel=_n_logs_blacklistcat_remove_params_channel,
    )
    _n_logs_blacklistcat_remove = LogsBlacklistcatRemove(
        description=LocalizedString('logs.blacklistcat.remove.description'),
        name=LocalizedString('logs.blacklistcat.remove.name'),
        params=_n_logs_blacklistcat_remove_params,
    )
    _n_logs_blacklistcat_show = LogsBlacklistcatShow(
        description=LocalizedString('logs.blacklistcat.show.description'),
        name=LocalizedString('logs.blacklistcat.show.name'),
    )
    _n_logs_blacklistcat = LogsBlacklistcat(
        add=_n_logs_blacklistcat_add,
        description=LocalizedString('logs.blacklistcat.description'),
        name=LocalizedString('logs.blacklistcat.name'),
        remove=_n_logs_blacklistcat_remove,
        show=_n_logs_blacklistcat_show,
    )
    _n_logs_blacklistr_add_params_role = LogsBlacklistrAddParamsRole(
        description=LocalizedString('logs.blacklistr.add.params.role.description'),
    )
    _n_logs_blacklistr_add_params = LogsBlacklistrAddParams(
        role=_n_logs_blacklistr_add_params_role,
    )
    _n_logs_blacklistr_add = LogsBlacklistrAdd(
        description=LocalizedString('logs.blacklistr.add.description'),
        name=LocalizedString('logs.blacklistr.add.name'),
        params=_n_logs_blacklistr_add_params,
    )
    _n_logs_blacklistr_remove_params_role = LogsBlacklistrRemoveParamsRole(
        description=LocalizedString('logs.blacklistr.remove.params.role.description'),
    )
    _n_logs_blacklistr_remove_params = LogsBlacklistrRemoveParams(
        role=_n_logs_blacklistr_remove_params_role,
    )
    _n_logs_blacklistr_remove = LogsBlacklistrRemove(
        description=LocalizedString('logs.blacklistr.remove.description'),
        name=LocalizedString('logs.blacklistr.remove.name'),
        params=_n_logs_blacklistr_remove_params,
    )
    _n_logs_blacklistr_show = LogsBlacklistrShow(
        description=LocalizedString('logs.blacklistr.show.description'),
        name=LocalizedString('logs.blacklistr.show.name'),
    )
    _n_logs_blacklistr = LogsBlacklistr(
        add=_n_logs_blacklistr_add,
        description=LocalizedString('logs.blacklistr.description'),
        name=LocalizedString('logs.blacklistr.name'),
        remove=_n_logs_blacklistr_remove,
        show=_n_logs_blacklistr_show,
    )
    _n_logs_blacklistu_add_params_user = LogsBlacklistuAddParamsUser(
        description=LocalizedString('logs.blacklistu.add.params.user.description'),
    )
    _n_logs_blacklistu_add_params = LogsBlacklistuAddParams(
        user=_n_logs_blacklistu_add_params_user,
    )
    _n_logs_blacklistu_add = LogsBlacklistuAdd(
        description=LocalizedString('logs.blacklistu.add.description'),
        name=LocalizedString('logs.blacklistu.add.name'),
        params=_n_logs_blacklistu_add_params,
    )
    _n_logs_blacklistu_remove_params_user = LogsBlacklistuRemoveParamsUser(
        description=LocalizedString('logs.blacklistu.remove.params.user.description'),
    )
    _n_logs_blacklistu_remove_params = LogsBlacklistuRemoveParams(
        user=_n_logs_blacklistu_remove_params_user,
    )
    _n_logs_blacklistu_remove = LogsBlacklistuRemove(
        description=LocalizedString('logs.blacklistu.remove.description'),
        name=LocalizedString('logs.blacklistu.remove.name'),
        params=_n_logs_blacklistu_remove_params,
    )
    _n_logs_blacklistu_show = LogsBlacklistuShow(
        description=LocalizedString('logs.blacklistu.show.description'),
        name=LocalizedString('logs.blacklistu.show.name'),
    )
    _n_logs_blacklistu = LogsBlacklistu(
        add=_n_logs_blacklistu_add,
        description=LocalizedString('logs.blacklistu.description'),
        name=LocalizedString('logs.blacklistu.name'),
        remove=_n_logs_blacklistu_remove,
        show=_n_logs_blacklistu_show,
    )
    _n_logs_blacklistv_add_params_channel = LogsBlacklistvAddParamsChannel(
        description=LocalizedString('logs.blacklistv.add.params.channel.description'),
    )
    _n_logs_blacklistv_add_params = LogsBlacklistvAddParams(
        channel=_n_logs_blacklistv_add_params_channel,
    )
    _n_logs_blacklistv_add = LogsBlacklistvAdd(
        description=LocalizedString('logs.blacklistv.add.description'),
        name=LocalizedString('logs.blacklistv.add.name'),
        params=_n_logs_blacklistv_add_params,
    )
    _n_logs_blacklistv_remove_params_channel = LogsBlacklistvRemoveParamsChannel(
        description=LocalizedString('logs.blacklistv.remove.params.channel.description'),
    )
    _n_logs_blacklistv_remove_params = LogsBlacklistvRemoveParams(
        channel=_n_logs_blacklistv_remove_params_channel,
    )
    _n_logs_blacklistv_remove = LogsBlacklistvRemove(
        description=LocalizedString('logs.blacklistv.remove.description'),
        name=LocalizedString('logs.blacklistv.remove.name'),
        params=_n_logs_blacklistv_remove_params,
    )
    _n_logs_blacklistv_show = LogsBlacklistvShow(
        description=LocalizedString('logs.blacklistv.show.description'),
        name=LocalizedString('logs.blacklistv.show.name'),
    )
    _n_logs_blacklistv = LogsBlacklistv(
        add=_n_logs_blacklistv_add,
        description=LocalizedString('logs.blacklistv.description'),
        name=LocalizedString('logs.blacklistv.name'),
        remove=_n_logs_blacklistv_remove,
        show=_n_logs_blacklistv_show,
    )
    _n_logs_configure = LogsConfigure(
        description=LocalizedString('logs.configure.description'),
        name=LocalizedString('logs.configure.name'),
    )
    _n_logs_guildChannelCreate_types_resolve = ResolveMap(
        'logs.guildChannelCreate.types.',
        {
            'category': LocalizedString('logs.guildChannelCreate.types.category'),
            'forum': LocalizedString('logs.guildChannelCreate.types.forum'),
            'news': LocalizedString('logs.guildChannelCreate.types.news'),
            'stage': LocalizedString('logs.guildChannelCreate.types.stage'),
            'text': LocalizedString('logs.guildChannelCreate.types.text'),
            'voice': LocalizedString('logs.guildChannelCreate.types.voice'),
        },
    )
    _n_logs_guildChannelCreate_types = LogsGuildChannelCreateTypes(
        category=LocalizedString('logs.guildChannelCreate.types.category'),
        forum=LocalizedString('logs.guildChannelCreate.types.forum'),
        news=LocalizedString('logs.guildChannelCreate.types.news'),
        resolve=_n_logs_guildChannelCreate_types_resolve,
        stage=LocalizedString('logs.guildChannelCreate.types.stage'),
        text=LocalizedString('logs.guildChannelCreate.types.text'),
        voice=LocalizedString('logs.guildChannelCreate.types.voice'),
    )
    _n_logs_guildChannelCreate = LogsGuildChannelCreate(
        category=LocalizedString('logs.guildChannelCreate.category'),
        created_at=LocalizedString('logs.guildChannelCreate.created_at'),
        created_by=LocalizedString('logs.guildChannelCreate.created_by'),
        name=LocalizedString('logs.guildChannelCreate.name'),
        permissionOverwriteAllowed=LocalizedString('logs.guildChannelCreate.permissionOverwriteAllowed'),
        permissionOverwriteDenied=LocalizedString('logs.guildChannelCreate.permissionOverwriteDenied'),
        permissionOverwriteNeutral=LocalizedString('logs.guildChannelCreate.permissionOverwriteNeutral'),
        permissionOverwriteTarget=LocalizedString('logs.guildChannelCreate.permissionOverwriteTarget'),
        permissionOverwrites=LocalizedString('logs.guildChannelCreate.permissionOverwrites'),
        title=LocalizedString('logs.guildChannelCreate.title'),
        topic=LocalizedString('logs.guildChannelCreate.topic'),
        type=LocalizedString('logs.guildChannelCreate.type'),
        types=_n_logs_guildChannelCreate_types,
    )
    _n_logs_guildChannelDelete_types_resolve = ResolveMap(
        'logs.guildChannelDelete.types.',
        {
            'category': LocalizedString('logs.guildChannelDelete.types.category'),
            'forum': LocalizedString('logs.guildChannelDelete.types.forum'),
            'stage': LocalizedString('logs.guildChannelDelete.types.stage'),
            'text': LocalizedString('logs.guildChannelDelete.types.text'),
            'voice': LocalizedString('logs.guildChannelDelete.types.voice'),
        },
    )
    _n_logs_guildChannelDelete_types = LogsGuildChannelDeleteTypes(
        category=LocalizedString('logs.guildChannelDelete.types.category'),
        forum=LocalizedString('logs.guildChannelDelete.types.forum'),
        resolve=_n_logs_guildChannelDelete_types_resolve,
        stage=LocalizedString('logs.guildChannelDelete.types.stage'),
        text=LocalizedString('logs.guildChannelDelete.types.text'),
        voice=LocalizedString('logs.guildChannelDelete.types.voice'),
    )
    _n_logs_guildChannelDelete = LogsGuildChannelDelete(
        category=LocalizedString('logs.guildChannelDelete.category'),
        created_at=LocalizedString('logs.guildChannelDelete.created_at'),
        deleted_by=LocalizedString('logs.guildChannelDelete.deleted_by'),
        name=LocalizedString('logs.guildChannelDelete.name'),
        permissionOverwriteAllowed=LocalizedString('logs.guildChannelDelete.permissionOverwriteAllowed'),
        permissionOverwriteDenied=LocalizedString('logs.guildChannelDelete.permissionOverwriteDenied'),
        permissionOverwriteNeutral=LocalizedString('logs.guildChannelDelete.permissionOverwriteNeutral'),
        permissionOverwriteTarget=LocalizedString('logs.guildChannelDelete.permissionOverwriteTarget'),
        permissionOverwrites=LocalizedString('logs.guildChannelDelete.permissionOverwrites'),
        title=LocalizedString('logs.guildChannelDelete.title'),
        topic=LocalizedString('logs.guildChannelDelete.topic'),
        type=LocalizedString('logs.guildChannelDelete.type'),
        types=_n_logs_guildChannelDelete_types,
    )
    _n_logs_guildChannelUpdate = LogsGuildChannelUpdate(
        category=LocalizedString('logs.guildChannelUpdate.category'),
        defaultAutoArchiveDuration=LocalizedString('logs.guildChannelUpdate.defaultAutoArchiveDuration'),
        defaultThreadAutoArchiveDuration=LocalizedString('logs.guildChannelUpdate.defaultThreadAutoArchiveDuration'),
        mention=LocalizedString('logs.guildChannelUpdate.mention'),
        name=LocalizedString('logs.guildChannelUpdate.name'),
        no=LocalizedString('logs.guildChannelUpdate.no'),
        nsfw=LocalizedString('logs.guildChannelUpdate.nsfw'),
        permissionOverwriteAddedAllow=LocalizedString('logs.guildChannelUpdate.permissionOverwriteAddedAllow'),
        permissionOverwriteAddedDeny=LocalizedString('logs.guildChannelUpdate.permissionOverwriteAddedDeny'),
        permissionOverwriteAddedNeutral=LocalizedString('logs.guildChannelUpdate.permissionOverwriteAddedNeutral'),
        permissionOverwriteAllowed=LocalizedString('logs.guildChannelUpdate.permissionOverwriteAllowed'),
        permissionOverwriteDenied=LocalizedString('logs.guildChannelUpdate.permissionOverwriteDenied'),
        permissionOverwriteModified=LocalizedString('logs.guildChannelUpdate.permissionOverwriteModified'),
        permissionOverwriteNeutral=LocalizedString('logs.guildChannelUpdate.permissionOverwriteNeutral'),
        permissionOverwriteNew=LocalizedString('logs.guildChannelUpdate.permissionOverwriteNew'),
        permissionOverwriteRemovedAllow=LocalizedString('logs.guildChannelUpdate.permissionOverwriteRemovedAllow'),
        permissionOverwriteRemovedDeny=LocalizedString('logs.guildChannelUpdate.permissionOverwriteRemovedDeny'),
        permissionOverwriteRemovedNeutral=LocalizedString('logs.guildChannelUpdate.permissionOverwriteRemovedNeutral'),
        permissionOverwriteTarget=LocalizedString('logs.guildChannelUpdate.permissionOverwriteTarget'),
        permissionOverwrites=LocalizedString('logs.guildChannelUpdate.permissionOverwrites'),
        slowmodeDelay=LocalizedString('logs.guildChannelUpdate.slowmodeDelay'),
        title=LocalizedString('logs.guildChannelUpdate.title'),
        topic=LocalizedString('logs.guildChannelUpdate.topic'),
        type=LocalizedString('logs.guildChannelUpdate.type'),
        updated_by=LocalizedString('logs.guildChannelUpdate.updated_by'),
        yes=LocalizedString('logs.guildChannelUpdate.yes'),
    )
    _n_logs_guildRoleCreate = LogsGuildRoleCreate(
        color=LocalizedString('logs.guildRoleCreate.color'),
        createdBy=LocalizedString('logs.guildRoleCreate.createdBy'),
        displayIcon=LocalizedString('logs.guildRoleCreate.displayIcon'),
        hoist=LocalizedString('logs.guildRoleCreate.hoist'),
        managed=LocalizedString('logs.guildRoleCreate.managed'),
        mentionable=LocalizedString('logs.guildRoleCreate.mentionable'),
        name=LocalizedString('logs.guildRoleCreate.name'),
        permissions=LocalizedString('logs.guildRoleCreate.permissions'),
        title=LocalizedString('logs.guildRoleCreate.title'),
    )
    _n_logs_guildRoleDelete = LogsGuildRoleDelete(
        deletedBy=LocalizedString('logs.guildRoleDelete.deletedBy'),
        name=LocalizedString('logs.guildRoleDelete.name'),
        permissions=LocalizedString('logs.guildRoleDelete.permissions'),
        title=LocalizedString('logs.guildRoleDelete.title'),
    )
    _n_logs_guildRoleUpdate = LogsGuildRoleUpdate(
        addedPermissions=LocalizedString('logs.guildRoleUpdate.addedPermissions'),
        color=LocalizedString('logs.guildRoleUpdate.color'),
        displayIcon=LocalizedString('logs.guildRoleUpdate.displayIcon'),
        hoistNoLonger=LocalizedString('logs.guildRoleUpdate.hoistNoLonger'),
        hoistNow=LocalizedString('logs.guildRoleUpdate.hoistNow'),
        icon=LocalizedString('logs.guildRoleUpdate.icon'),
        managedNoLonger=LocalizedString('logs.guildRoleUpdate.managedNoLonger'),
        managedNow=LocalizedString('logs.guildRoleUpdate.managedNow'),
        mentionableNoLonger=LocalizedString('logs.guildRoleUpdate.mentionableNoLonger'),
        mentionableNow=LocalizedString('logs.guildRoleUpdate.mentionableNow'),
        name=LocalizedString('logs.guildRoleUpdate.name'),
        removedPermissions=LocalizedString('logs.guildRoleUpdate.removedPermissions'),
        title=LocalizedString('logs.guildRoleUpdate.title'),
        updatedBy=LocalizedString('logs.guildRoleUpdate.updatedBy'),
    )
    _n_logs_guildUpdate_defaultNotificationsLocales = LogsGuildUpdateDefaultNotificationsLocales(
        allMembers=LocalizedString('logs.guildUpdate.defaultNotificationsLocales.allMembers'),
        all_members=LocalizedString('logs.guildUpdate.defaultNotificationsLocales.all_members'),
        onlyMentions=LocalizedString('logs.guildUpdate.defaultNotificationsLocales.onlyMentions'),
    )
    _n_logs_guildUpdate_discoverySplashLocales = LogsGuildUpdateDiscoverySplashLocales(
        url=LocalizedString('logs.guildUpdate.discoverySplashLocales.url'),
    )
    _n_logs_guildUpdate_explicitContentFilterLocales = LogsGuildUpdateExplicitContentFilterLocales(
        allMembers=LocalizedString('logs.guildUpdate.explicitContentFilterLocales.allMembers'),
        all_members=LocalizedString('logs.guildUpdate.explicitContentFilterLocales.all_members'),
        disabled=LocalizedString('logs.guildUpdate.explicitContentFilterLocales.disabled'),
        noRole=LocalizedString('logs.guildUpdate.explicitContentFilterLocales.noRole'),
        no_role=LocalizedString('logs.guildUpdate.explicitContentFilterLocales.no_role'),
    )
    _n_logs_guildUpdate_featuresLocales_resolve = ResolveMap(
        'logs.guildUpdate.featuresLocales.',
        {
            'ANIMATED_BANNER': LocalizedString('logs.guildUpdate.featuresLocales.ANIMATED_BANNER'),
            'ANIMATED_ICON': LocalizedString('logs.guildUpdate.featuresLocales.ANIMATED_ICON'),
            'APPLICATION_COMMAND_PERMISSIONS_V2': LocalizedString('logs.guildUpdate.featuresLocales.APPLICATION_COMMAND_PERMISSIONS_V2'),
            'AUTO_MODERATION': LocalizedString('logs.guildUpdate.featuresLocales.AUTO_MODERATION'),
            'BANNER': LocalizedString('logs.guildUpdate.featuresLocales.BANNER'),
            'COMMUNITY': LocalizedString('logs.guildUpdate.featuresLocales.COMMUNITY'),
            'CREATOR_MONETIZATION_ANALYTICS': LocalizedString('logs.guildUpdate.featuresLocales.CREATOR_MONETIZATION_ANALYTICS'),
            'CREATOR_STORE_PAGE': LocalizedString('logs.guildUpdate.featuresLocales.CREATOR_STORE_PAGE'),
            'DEVELOPER_SUPPORT_SERVER': LocalizedString('logs.guildUpdate.featuresLocales.DEVELOPER_SUPPORT_SERVER'),
            'DISCOVERABLE': LocalizedString('logs.guildUpdate.featuresLocales.DISCOVERABLE'),
            'FEATURABLE': LocalizedString('logs.guildUpdate.featuresLocales.FEATURABLE'),
            'INVITES_DISABLED': LocalizedString('logs.guildUpdate.featuresLocales.INVITES_DISABLED'),
            'INVITE_SPLASH': LocalizedString('logs.guildUpdate.featuresLocales.INVITE_SPLASH'),
            'MEMBER_VERIFICATION_GATE_ENABLED': LocalizedString('logs.guildUpdate.featuresLocales.MEMBER_VERIFICATION_GATE_ENABLED'),
            'MORE_SOUNDBOARD': LocalizedString('logs.guildUpdate.featuresLocales.MORE_SOUNDBOARD'),
            'MORE_STICKERS': LocalizedString('logs.guildUpdate.featuresLocales.MORE_STICKERS'),
            'NEWS': LocalizedString('logs.guildUpdate.featuresLocales.NEWS'),
            'PARTNERED': LocalizedString('logs.guildUpdate.featuresLocales.PARTNERED'),
            'PREVIEW_ENABLED': LocalizedString('logs.guildUpdate.featuresLocales.PREVIEW_ENABLED'),
            'RAID_ALERTS_DISABLED': LocalizedString('logs.guildUpdate.featuresLocales.RAID_ALERTS_DISABLED'),
            'ROLE_ICONS': LocalizedString('logs.guildUpdate.featuresLocales.ROLE_ICONS'),
            'ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE': LocalizedString('logs.guildUpdate.featuresLocales.ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE'),
            'ROLE_SUBSCRIPTIONS_ENABLED': LocalizedString('logs.guildUpdate.featuresLocales.ROLE_SUBSCRIPTIONS_ENABLED'),
            'SOUNDBOARD': LocalizedString('logs.guildUpdate.featuresLocales.SOUNDBOARD'),
            'TICKETED_EVENTS_ENABLED': LocalizedString('logs.guildUpdate.featuresLocales.TICKETED_EVENTS_ENABLED'),
            'VANITY_URL': LocalizedString('logs.guildUpdate.featuresLocales.VANITY_URL'),
            'VERIFIED': LocalizedString('logs.guildUpdate.featuresLocales.VERIFIED'),
            'VIP_REGIONS': LocalizedString('logs.guildUpdate.featuresLocales.VIP_REGIONS'),
            'WELCOME_SCREEN_ENABLED': LocalizedString('logs.guildUpdate.featuresLocales.WELCOME_SCREEN_ENABLED'),
        },
    )
    _n_logs_guildUpdate_featuresLocales = LogsGuildUpdateFeaturesLocales(
        ANIMATED_BANNER=LocalizedString('logs.guildUpdate.featuresLocales.ANIMATED_BANNER'),
        ANIMATED_ICON=LocalizedString('logs.guildUpdate.featuresLocales.ANIMATED_ICON'),
        APPLICATION_COMMAND_PERMISSIONS_V2=LocalizedString('logs.guildUpdate.featuresLocales.APPLICATION_COMMAND_PERMISSIONS_V2'),
        AUTO_MODERATION=LocalizedString('logs.guildUpdate.featuresLocales.AUTO_MODERATION'),
        BANNER=LocalizedString('logs.guildUpdate.featuresLocales.BANNER'),
        COMMUNITY=LocalizedString('logs.guildUpdate.featuresLocales.COMMUNITY'),
        CREATOR_MONETIZATION_ANALYTICS=LocalizedString('logs.guildUpdate.featuresLocales.CREATOR_MONETIZATION_ANALYTICS'),
        CREATOR_STORE_PAGE=LocalizedString('logs.guildUpdate.featuresLocales.CREATOR_STORE_PAGE'),
        DEVELOPER_SUPPORT_SERVER=LocalizedString('logs.guildUpdate.featuresLocales.DEVELOPER_SUPPORT_SERVER'),
        DISCOVERABLE=LocalizedString('logs.guildUpdate.featuresLocales.DISCOVERABLE'),
        FEATURABLE=LocalizedString('logs.guildUpdate.featuresLocales.FEATURABLE'),
        INVITES_DISABLED=LocalizedString('logs.guildUpdate.featuresLocales.INVITES_DISABLED'),
        INVITE_SPLASH=LocalizedString('logs.guildUpdate.featuresLocales.INVITE_SPLASH'),
        MEMBER_VERIFICATION_GATE_ENABLED=LocalizedString('logs.guildUpdate.featuresLocales.MEMBER_VERIFICATION_GATE_ENABLED'),
        MORE_SOUNDBOARD=LocalizedString('logs.guildUpdate.featuresLocales.MORE_SOUNDBOARD'),
        MORE_STICKERS=LocalizedString('logs.guildUpdate.featuresLocales.MORE_STICKERS'),
        NEWS=LocalizedString('logs.guildUpdate.featuresLocales.NEWS'),
        PARTNERED=LocalizedString('logs.guildUpdate.featuresLocales.PARTNERED'),
        PREVIEW_ENABLED=LocalizedString('logs.guildUpdate.featuresLocales.PREVIEW_ENABLED'),
        RAID_ALERTS_DISABLED=LocalizedString('logs.guildUpdate.featuresLocales.RAID_ALERTS_DISABLED'),
        ROLE_ICONS=LocalizedString('logs.guildUpdate.featuresLocales.ROLE_ICONS'),
        ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE=LocalizedString('logs.guildUpdate.featuresLocales.ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE'),
        ROLE_SUBSCRIPTIONS_ENABLED=LocalizedString('logs.guildUpdate.featuresLocales.ROLE_SUBSCRIPTIONS_ENABLED'),
        SOUNDBOARD=LocalizedString('logs.guildUpdate.featuresLocales.SOUNDBOARD'),
        TICKETED_EVENTS_ENABLED=LocalizedString('logs.guildUpdate.featuresLocales.TICKETED_EVENTS_ENABLED'),
        VANITY_URL=LocalizedString('logs.guildUpdate.featuresLocales.VANITY_URL'),
        VERIFIED=LocalizedString('logs.guildUpdate.featuresLocales.VERIFIED'),
        VIP_REGIONS=LocalizedString('logs.guildUpdate.featuresLocales.VIP_REGIONS'),
        WELCOME_SCREEN_ENABLED=LocalizedString('logs.guildUpdate.featuresLocales.WELCOME_SCREEN_ENABLED'),
        resolve=_n_logs_guildUpdate_featuresLocales_resolve,
    )
    _n_logs_guildUpdate_iconLocales = LogsGuildUpdateIconLocales(
        noIcon=LocalizedString('logs.guildUpdate.iconLocales.noIcon'),
        url=LocalizedString('logs.guildUpdate.iconLocales.url'),
    )
    _n_logs_guildUpdate_invitesPausedUntilLocales = LogsGuildUpdateInvitesPausedUntilLocales(
        notPaused=LocalizedString('logs.guildUpdate.invitesPausedUntilLocales.notPaused'),
    )
    _n_logs_guildUpdate_nsfwLevelLocales = LogsGuildUpdateNsfwLevelLocales(
        ageRegistered=LocalizedString('logs.guildUpdate.nsfwLevelLocales.ageRegistered'),
        default=LocalizedString('logs.guildUpdate.nsfwLevelLocales.default'),
        explicit=LocalizedString('logs.guildUpdate.nsfwLevelLocales.explicit'),
        safe=LocalizedString('logs.guildUpdate.nsfwLevelLocales.safe'),
    )
    _n_logs_guildUpdate_preferredLocaleLocales_resolve = ResolveMap(
        'logs.guildUpdate.preferredLocaleLocales.',
        {
            'bg': LocalizedString('logs.guildUpdate.preferredLocaleLocales.bg'),
            'cs': LocalizedString('logs.guildUpdate.preferredLocaleLocales.cs'),
            'da': LocalizedString('logs.guildUpdate.preferredLocaleLocales.da'),
            'de': LocalizedString('logs.guildUpdate.preferredLocaleLocales.de'),
            'el': LocalizedString('logs.guildUpdate.preferredLocaleLocales.el'),
            'en-GB': LocalizedString('logs.guildUpdate.preferredLocaleLocales.en-GB'),
            'en-US': LocalizedString('logs.guildUpdate.preferredLocaleLocales.en-US'),
            'es-419': LocalizedString('logs.guildUpdate.preferredLocaleLocales.es-419'),
            'es-ES': LocalizedString('logs.guildUpdate.preferredLocaleLocales.es-ES'),
            'fi': LocalizedString('logs.guildUpdate.preferredLocaleLocales.fi'),
            'fr': LocalizedString('logs.guildUpdate.preferredLocaleLocales.fr'),
            'hi': LocalizedString('logs.guildUpdate.preferredLocaleLocales.hi'),
            'hr': LocalizedString('logs.guildUpdate.preferredLocaleLocales.hr'),
            'hu': LocalizedString('logs.guildUpdate.preferredLocaleLocales.hu'),
            'id': LocalizedString('logs.guildUpdate.preferredLocaleLocales.id'),
            'it': LocalizedString('logs.guildUpdate.preferredLocaleLocales.it'),
            'ko': LocalizedString('logs.guildUpdate.preferredLocaleLocales.ko'),
            'lt': LocalizedString('logs.guildUpdate.preferredLocaleLocales.lt'),
            'nl': LocalizedString('logs.guildUpdate.preferredLocaleLocales.nl'),
            'no': LocalizedString('logs.guildUpdate.preferredLocaleLocales.no'),
            'pl': LocalizedString('logs.guildUpdate.preferredLocaleLocales.pl'),
            'pt-BR': LocalizedString('logs.guildUpdate.preferredLocaleLocales.pt-BR'),
            'ro': LocalizedString('logs.guildUpdate.preferredLocaleLocales.ro'),
            'sv-SE': LocalizedString('logs.guildUpdate.preferredLocaleLocales.sv-SE'),
            'th': LocalizedString('logs.guildUpdate.preferredLocaleLocales.th'),
            'tr': LocalizedString('logs.guildUpdate.preferredLocaleLocales.tr'),
            'uk': LocalizedString('logs.guildUpdate.preferredLocaleLocales.uk'),
            'vi': LocalizedString('logs.guildUpdate.preferredLocaleLocales.vi'),
            'zh-CN': LocalizedString('logs.guildUpdate.preferredLocaleLocales.zh-CN'),
            'zh-TW': LocalizedString('logs.guildUpdate.preferredLocaleLocales.zh-TW'),
        },
    )
    _n_logs_guildUpdate_preferredLocaleLocales = LogsGuildUpdatePreferredLocaleLocales(
        bg=LocalizedString('logs.guildUpdate.preferredLocaleLocales.bg'),
        cs=LocalizedString('logs.guildUpdate.preferredLocaleLocales.cs'),
        da=LocalizedString('logs.guildUpdate.preferredLocaleLocales.da'),
        de=LocalizedString('logs.guildUpdate.preferredLocaleLocales.de'),
        el=LocalizedString('logs.guildUpdate.preferredLocaleLocales.el'),
        en_GB=LocalizedString('logs.guildUpdate.preferredLocaleLocales.en-GB'),
        en_US=LocalizedString('logs.guildUpdate.preferredLocaleLocales.en-US'),
        es_419=LocalizedString('logs.guildUpdate.preferredLocaleLocales.es-419'),
        es_ES=LocalizedString('logs.guildUpdate.preferredLocaleLocales.es-ES'),
        fi=LocalizedString('logs.guildUpdate.preferredLocaleLocales.fi'),
        fr=LocalizedString('logs.guildUpdate.preferredLocaleLocales.fr'),
        hi=LocalizedString('logs.guildUpdate.preferredLocaleLocales.hi'),
        hr=LocalizedString('logs.guildUpdate.preferredLocaleLocales.hr'),
        hu=LocalizedString('logs.guildUpdate.preferredLocaleLocales.hu'),
        id=LocalizedString('logs.guildUpdate.preferredLocaleLocales.id'),
        it=LocalizedString('logs.guildUpdate.preferredLocaleLocales.it'),
        ko=LocalizedString('logs.guildUpdate.preferredLocaleLocales.ko'),
        lt=LocalizedString('logs.guildUpdate.preferredLocaleLocales.lt'),
        nl=LocalizedString('logs.guildUpdate.preferredLocaleLocales.nl'),
        no=LocalizedString('logs.guildUpdate.preferredLocaleLocales.no'),
        pl=LocalizedString('logs.guildUpdate.preferredLocaleLocales.pl'),
        pt_BR=LocalizedString('logs.guildUpdate.preferredLocaleLocales.pt-BR'),
        resolve=_n_logs_guildUpdate_preferredLocaleLocales_resolve,
        ro=LocalizedString('logs.guildUpdate.preferredLocaleLocales.ro'),
        sv_SE=LocalizedString('logs.guildUpdate.preferredLocaleLocales.sv-SE'),
        th=LocalizedString('logs.guildUpdate.preferredLocaleLocales.th'),
        tr=LocalizedString('logs.guildUpdate.preferredLocaleLocales.tr'),
        uk=LocalizedString('logs.guildUpdate.preferredLocaleLocales.uk'),
        vi=LocalizedString('logs.guildUpdate.preferredLocaleLocales.vi'),
        zh_CN=LocalizedString('logs.guildUpdate.preferredLocaleLocales.zh-CN'),
        zh_TW=LocalizedString('logs.guildUpdate.preferredLocaleLocales.zh-TW'),
    )
    _n_logs_guildUpdate_premiumProgressBarEnabled = LogsGuildUpdatePremiumProgressBarEnabled(
        activated=LocalizedString('logs.guildUpdate.premiumProgressBarEnabled.activated'),
        deactivated=LocalizedString('logs.guildUpdate.premiumProgressBarEnabled.deactivated'),
    )
    _n_logs_guildUpdate_premiumProgressBarLocales = LogsGuildUpdatePremiumProgressBarLocales(
        activated=LocalizedString('logs.guildUpdate.premiumProgressBarLocales.activated'),
        deactivated=LocalizedString('logs.guildUpdate.premiumProgressBarLocales.deactivated'),
    )
    _n_logs_guildUpdate_unavailableLocales = LogsGuildUpdateUnavailableLocales(
        available=LocalizedString('logs.guildUpdate.unavailableLocales.available'),
        unavailable=LocalizedString('logs.guildUpdate.unavailableLocales.unavailable'),
    )
    _n_logs_guildUpdate_verificationLevelLocales = LogsGuildUpdateVerificationLevelLocales(
        high=LocalizedString('logs.guildUpdate.verificationLevelLocales.high'),
        highest=LocalizedString('logs.guildUpdate.verificationLevelLocales.highest'),
        low=LocalizedString('logs.guildUpdate.verificationLevelLocales.low'),
        medium=LocalizedString('logs.guildUpdate.verificationLevelLocales.medium'),
        none=LocalizedString('logs.guildUpdate.verificationLevelLocales.none'),
    )
    _n_logs_guildUpdate = LogsGuildUpdate(
        addedEmojis=LocalizedString('logs.guildUpdate.addedEmojis'),
        addedFeatures=LocalizedString('logs.guildUpdate.addedFeatures'),
        afkChannel=LocalizedString('logs.guildUpdate.afkChannel'),
        afkTimeout=LocalizedString('logs.guildUpdate.afkTimeout'),
        banner=LocalizedString('logs.guildUpdate.banner'),
        defaultNotifications=LocalizedString('logs.guildUpdate.defaultNotifications'),
        defaultNotificationsLocales=_n_logs_guildUpdate_defaultNotificationsLocales,
        description=LocalizedString('logs.guildUpdate.description'),
        discoverySplash=LocalizedString('logs.guildUpdate.discoverySplash'),
        discoverySplashLocales=_n_logs_guildUpdate_discoverySplashLocales,
        emojiLimit=LocalizedString('logs.guildUpdate.emojiLimit'),
        explicitContentFilter=LocalizedString('logs.guildUpdate.explicitContentFilter'),
        explicitContentFilterLocales=_n_logs_guildUpdate_explicitContentFilterLocales,
        featuresLocales=_n_logs_guildUpdate_featuresLocales,
        filesizeLimit=LocalizedString('logs.guildUpdate.filesizeLimit'),
        icon=LocalizedString('logs.guildUpdate.icon'),
        iconLocales=_n_logs_guildUpdate_iconLocales,
        invitesPausedUntil=LocalizedString('logs.guildUpdate.invitesPausedUntil'),
        invitesPausedUntilLocales=_n_logs_guildUpdate_invitesPausedUntilLocales,
        maxMembers=LocalizedString('logs.guildUpdate.maxMembers'),
        maxPresences=LocalizedString('logs.guildUpdate.maxPresences'),
        maxVideoChannelUsers=LocalizedString('logs.guildUpdate.maxVideoChannelUsers'),
        name=LocalizedString('logs.guildUpdate.name'),
        none=LocalizedString('logs.guildUpdate.none'),
        nsfwLevel=LocalizedString('logs.guildUpdate.nsfwLevel'),
        nsfwLevelLocales=_n_logs_guildUpdate_nsfwLevelLocales,
        owner=LocalizedString('logs.guildUpdate.owner'),
        preferredLocale=LocalizedString('logs.guildUpdate.preferredLocale'),
        preferredLocaleLocales=_n_logs_guildUpdate_preferredLocaleLocales,
        premiumProgressBarEnabled=_n_logs_guildUpdate_premiumProgressBarEnabled,
        premiumProgressBarLocales=_n_logs_guildUpdate_premiumProgressBarLocales,
        premiumSubscriberRole=LocalizedString('logs.guildUpdate.premiumSubscriberRole'),
        premiumSubscribers=LocalizedString('logs.guildUpdate.premiumSubscribers'),
        premiumTier=LocalizedString('logs.guildUpdate.premiumTier'),
        publicUpdatesChannel=LocalizedString('logs.guildUpdate.publicUpdatesChannel'),
        removedEmojis=LocalizedString('logs.guildUpdate.removedEmojis'),
        removedFeatures=LocalizedString('logs.guildUpdate.removedFeatures'),
        rulesChannel=LocalizedString('logs.guildUpdate.rulesChannel'),
        safetyAlertsChannel=LocalizedString('logs.guildUpdate.safetyAlertsChannel'),
        title=LocalizedString('logs.guildUpdate.title'),
        unavailableLocales=_n_logs_guildUpdate_unavailableLocales,
        verificationLevel=LocalizedString('logs.guildUpdate.verificationLevel'),
        verificationLevelLocales=_n_logs_guildUpdate_verificationLevelLocales,
    )
    _n_logs_guild_channelCreate = LogsGuild_channelCreate(
        category=LocalizedString('logs.guild_channelCreate.category'),
        created_at=LocalizedString('logs.guild_channelCreate.created_at'),
        created_by=LocalizedString('logs.guild_channelCreate.created_by'),
        name=LocalizedString('logs.guild_channelCreate.name'),
        permissionOverwrites=LocalizedString('logs.guild_channelCreate.permissionOverwrites'),
        title=LocalizedString('logs.guild_channelCreate.title'),
        topic=LocalizedString('logs.guild_channelCreate.topic'),
        type=LocalizedString('logs.guild_channelCreate.type'),
        types=LocalizedString('logs.guild_channelCreate.types.'),
    )
    _n_logs_guild_channelDelete = LogsGuild_channelDelete(
        category=LocalizedString('logs.guild_channelDelete.category'),
        created_at=LocalizedString('logs.guild_channelDelete.created_at'),
        deleted_by=LocalizedString('logs.guild_channelDelete.deleted_by'),
        name=LocalizedString('logs.guild_channelDelete.name'),
        permissionOverwriteAllowed=LocalizedString('logs.guild_channelDelete.permissionOverwriteAllowed'),
        permissionOverwriteDenied=LocalizedString('logs.guild_channelDelete.permissionOverwriteDenied'),
        permissionOverwriteTarget=LocalizedString('logs.guild_channelDelete.permissionOverwriteTarget'),
        permissionOverwrites=LocalizedString('logs.guild_channelDelete.permissionOverwrites'),
        title=LocalizedString('logs.guild_channelDelete.title'),
        topic=LocalizedString('logs.guild_channelDelete.topic'),
        type=LocalizedString('logs.guild_channelDelete.type'),
        types=LocalizedString('logs.guild_channelDelete.types.'),
    )
    _n_logs_guild_channelUpdate = LogsGuild_channelUpdate(
        category=LocalizedString('logs.guild_channelUpdate.category'),
        defaultAutoArchiveDuration=LocalizedString('logs.guild_channelUpdate.defaultAutoArchiveDuration'),
        defaultThreadAutoArchiveDuration=LocalizedString('logs.guild_channelUpdate.defaultThreadAutoArchiveDuration'),
        mention=LocalizedString('logs.guild_channelUpdate.mention'),
        name=LocalizedString('logs.guild_channelUpdate.name'),
        no=LocalizedString('logs.guild_channelUpdate.no'),
        nsfw=LocalizedString('logs.guild_channelUpdate.nsfw'),
        permissionOverwriteAddedAllow=LocalizedString('logs.guild_channelUpdate.permissionOverwriteAddedAllow'),
        permissionOverwriteAddedDeny=LocalizedString('logs.guild_channelUpdate.permissionOverwriteAddedDeny'),
        permissionOverwriteAddedNeutral=LocalizedString('logs.guild_channelUpdate.permissionOverwriteAddedNeutral'),
        permissionOverwriteAllowed=LocalizedString('logs.guild_channelUpdate.permissionOverwriteAllowed'),
        permissionOverwriteDenied=LocalizedString('logs.guild_channelUpdate.permissionOverwriteDenied'),
        permissionOverwriteModified=LocalizedString('logs.guild_channelUpdate.permissionOverwriteModified'),
        permissionOverwriteNeutral=LocalizedString('logs.guild_channelUpdate.permissionOverwriteNeutral'),
        permissionOverwriteNew=LocalizedString('logs.guild_channelUpdate.permissionOverwriteNew'),
        permissionOverwriteRemoved=LocalizedString('logs.guild_channelUpdate.permissionOverwriteRemoved'),
        permissionOverwriteRemovedAllow=LocalizedString('logs.guild_channelUpdate.permissionOverwriteRemovedAllow'),
        permissionOverwriteRemovedDeny=LocalizedString('logs.guild_channelUpdate.permissionOverwriteRemovedDeny'),
        permissionOverwriteRemovedNeutral=LocalizedString('logs.guild_channelUpdate.permissionOverwriteRemovedNeutral'),
        slowmodeDelay=LocalizedString('logs.guild_channelUpdate.slowmodeDelay'),
        title=LocalizedString('logs.guild_channelUpdate.title'),
        topic=LocalizedString('logs.guild_channelUpdate.topic'),
        type=LocalizedString('logs.guild_channelUpdate.type'),
        types=LocalizedString('logs.guild_channelUpdate.types.'),
        updated_by=LocalizedString('logs.guild_channelUpdate.updated_by'),
        yes=LocalizedString('logs.guild_channelUpdate.yes'),
    )
    _n_logs_inviteCreate_expiresLocales = LogsInviteCreateExpiresLocales(
        never=LocalizedString('logs.inviteCreate.expiresLocales.never'),
    )
    _n_logs_inviteCreate_maxUsesLocales = LogsInviteCreateMaxUsesLocales(
        infinite=LocalizedString('logs.inviteCreate.maxUsesLocales.infinite'),
    )
    _n_logs_inviteCreate_targetTypeLocales_resolve = ResolveMap(
        'logs.inviteCreate.targetTypeLocales.',
        {
            '"InviteTarget.embeddedApplication"': LocalizedString('logs.inviteCreate.targetTypeLocales."InviteTarget.embeddedApplication"'),
            '"InviteTarget.stream"': LocalizedString('logs.inviteCreate.targetTypeLocales."InviteTarget.stream"'),
            '"InviteTarget.unknown"': LocalizedString('logs.inviteCreate.targetTypeLocales."InviteTarget.unknown"'),
        },
    )
    _n_logs_inviteCreate_targetTypeLocales = LogsInviteCreateTargetTypeLocales(
        InviteTarget_embeddedApplication=LocalizedString('logs.inviteCreate.targetTypeLocales."InviteTarget.embeddedApplication"'),
        InviteTarget_stream=LocalizedString('logs.inviteCreate.targetTypeLocales."InviteTarget.stream"'),
        InviteTarget_unknown=LocalizedString('logs.inviteCreate.targetTypeLocales."InviteTarget.unknown"'),
        resolve=_n_logs_inviteCreate_targetTypeLocales_resolve,
    )
    _n_logs_inviteCreate = LogsInviteCreate(
        channel=LocalizedString('logs.inviteCreate.channel'),
        createdBy=LocalizedString('logs.inviteCreate.createdBy'),
        expires=LocalizedString('logs.inviteCreate.expires'),
        expiresLocales=_n_logs_inviteCreate_expiresLocales,
        invite=LocalizedString('logs.inviteCreate.invite'),
        maxUsesLocales=_n_logs_inviteCreate_maxUsesLocales,
        max_uses=LocalizedString('logs.inviteCreate.max_uses'),
        scheduledEvent=LocalizedString('logs.inviteCreate.scheduledEvent'),
        targetApplication=LocalizedString('logs.inviteCreate.targetApplication'),
        targetTypeLocales=_n_logs_inviteCreate_targetTypeLocales,
        targetUser=LocalizedString('logs.inviteCreate.targetUser'),
        temporary=LocalizedString('logs.inviteCreate.temporary'),
        title=LocalizedString('logs.inviteCreate.title'),
    )
    _n_logs_inviteDelete = LogsInviteDelete(
        invite=LocalizedString('logs.inviteDelete.invite'),
        title=LocalizedString('logs.inviteDelete.title'),
    )
    _n_logs_memberBan = LogsMemberBan(
        banned_by=LocalizedString('logs.memberBan.banned_by'),
        name=LocalizedString('logs.memberBan.name'),
        title=LocalizedString('logs.memberBan.title'),
    )
    _n_logs_memberJoin = LogsMemberJoin(
        name=LocalizedString('logs.memberJoin.name'),
        title=LocalizedString('logs.memberJoin.title'),
    )
    _n_logs_memberRemove = LogsMemberRemove(
        name=LocalizedString('logs.memberRemove.name'),
        roles=LocalizedString('logs.memberRemove.roles'),
        title=LocalizedString('logs.memberRemove.title'),
    )
    _n_logs_memberUnban = LogsMemberUnban(
        name=LocalizedString('logs.memberUnban.name'),
        title=LocalizedString('logs.memberUnban.title'),
        unbanned_by=LocalizedString('logs.memberUnban.unbanned_by'),
    )
    _n_logs_memberUpdate_guildAvatarLocales = LogsMemberUpdateGuildAvatarLocales(
        none=LocalizedString('logs.memberUpdate.guildAvatarLocales.none'),
        url=LocalizedString('logs.memberUpdate.guildAvatarLocales.url'),
    )
    _n_logs_memberUpdate = LogsMemberUpdate(
        addedRoles=LocalizedString('logs.memberUpdate.addedRoles'),
        banner=LocalizedString('logs.memberUpdate.banner'),
        displayName=LocalizedString('logs.memberUpdate.displayName'),
        guildAvatar=LocalizedString('logs.memberUpdate.guildAvatar'),
        guildAvatarLocales=_n_logs_memberUpdate_guildAvatarLocales,
        name=LocalizedString('logs.memberUpdate.name'),
        pending=LocalizedString('logs.memberUpdate.pending'),
        pendingRemoved=LocalizedString('logs.memberUpdate.pendingRemoved'),
        removedRoles=LocalizedString('logs.memberUpdate.removedRoles'),
        timeout=LocalizedString('logs.memberUpdate.timeout'),
        timeoutRemoved=LocalizedString('logs.memberUpdate.timeoutRemoved'),
        title=LocalizedString('logs.memberUpdate.title'),
    )
    _n_logs_messageDelete = LogsMessageDelete(
        attachments=LocalizedString('logs.messageDelete.attachments'),
        content=LocalizedString('logs.messageDelete.content'),
        deletedBy=LocalizedString('logs.messageDelete.deletedBy'),
        embeds=LocalizedString('logs.messageDelete.embeds'),
        name=LocalizedString('logs.messageDelete.name'),
        title=LocalizedString('logs.messageDelete.title'),
        urlNotAvaiableLocale=LocalizedString('logs.messageDelete.urlNotAvaiableLocale'),
        url_not_available_locale=LocalizedString('logs.messageDelete.url_not_available_locale'),
    )
    _n_logs_messageEdit = LogsMessageEdit(
        addedAttachments=LocalizedString('logs.messageEdit.addedAttachments'),
        content=LocalizedString('logs.messageEdit.content'),
        diff=LocalizedString('logs.messageEdit.diff'),
        ellipsis=LocalizedString('logs.messageEdit.ellipsis'),
        embeds=LocalizedString('logs.messageEdit.embeds'),
        name=LocalizedString('logs.messageEdit.name'),
        removedAttachments=LocalizedString('logs.messageEdit.removedAttachments'),
        title=LocalizedString('logs.messageEdit.title'),
        tooLongNotice=LocalizedString('logs.messageEdit.tooLongNotice'),
        truncatedNotice=LocalizedString('logs.messageEdit.truncatedNotice'),
        urlNotAvaiableLocale=LocalizedString('logs.messageEdit.urlNotAvaiableLocale'),
        url_not_available_locale=LocalizedString('logs.messageEdit.url_not_available_locale'),
    )
    _n_logs_permissions_resolve = ResolveMap(
        'logs.permissions.',
        {
            'add_reaction': LocalizedString('logs.permissions.add_reaction'),
            'add_reactions': LocalizedString('logs.permissions.add_reactions'),
            'administrator': LocalizedString('logs.permissions.administrator'),
            'attach_files': LocalizedString('logs.permissions.attach_files'),
            'ban_members': LocalizedString('logs.permissions.ban_members'),
            'change_nickname': LocalizedString('logs.permissions.change_nickname'),
            'connect': LocalizedString('logs.permissions.connect'),
            'create_events': LocalizedString('logs.permissions.create_events'),
            'create_expressions': LocalizedString('logs.permissions.create_expressions'),
            'create_instant_invite': LocalizedString('logs.permissions.create_instant_invite'),
            'create_polls': LocalizedString('logs.permissions.create_polls'),
            'create_private_threads': LocalizedString('logs.permissions.create_private_threads'),
            'create_public_threads': LocalizedString('logs.permissions.create_public_threads'),
            'deafen_members': LocalizedString('logs.permissions.deafen_members'),
            'embed_links': LocalizedString('logs.permissions.embed_links'),
            'external_emojis': LocalizedString('logs.permissions.external_emojis'),
            'external_stickers': LocalizedString('logs.permissions.external_stickers'),
            'kick_members': LocalizedString('logs.permissions.kick_members'),
            'manage_channels': LocalizedString('logs.permissions.manage_channels'),
            'manage_emojis': LocalizedString('logs.permissions.manage_emojis'),
            'manage_emojis_and_stickers': LocalizedString('logs.permissions.manage_emojis_and_stickers'),
            'manage_events': LocalizedString('logs.permissions.manage_events'),
            'manage_expressions': LocalizedString('logs.permissions.manage_expressions'),
            'manage_guild': LocalizedString('logs.permissions.manage_guild'),
            'manage_messages': LocalizedString('logs.permissions.manage_messages'),
            'manage_nicknames': LocalizedString('logs.permissions.manage_nicknames'),
            'manage_permissions': LocalizedString('logs.permissions.manage_permissions'),
            'manage_roles': LocalizedString('logs.permissions.manage_roles'),
            'manage_stickers': LocalizedString('logs.permissions.manage_stickers'),
            'manage_threads': LocalizedString('logs.permissions.manage_threads'),
            'manage_webhooks': LocalizedString('logs.permissions.manage_webhooks'),
            'mention_everyone': LocalizedString('logs.permissions.mention_everyone'),
            'moderate_members': LocalizedString('logs.permissions.moderate_members'),
            'move_members': LocalizedString('logs.permissions.move_members'),
            'mute_members': LocalizedString('logs.permissions.mute_members'),
            'priority_speaker': LocalizedString('logs.permissions.priority_speaker'),
            'read_message_history': LocalizedString('logs.permissions.read_message_history'),
            'read_messages': LocalizedString('logs.permissions.read_messages'),
            'request_to_speak': LocalizedString('logs.permissions.request_to_speak'),
            'send_messages': LocalizedString('logs.permissions.send_messages'),
            'send_messages_in_threads': LocalizedString('logs.permissions.send_messages_in_threads'),
            'send_polls': LocalizedString('logs.permissions.send_polls'),
            'send_tts_messages': LocalizedString('logs.permissions.send_tts_messages'),
            'send_voice_messages': LocalizedString('logs.permissions.send_voice_messages'),
            'speak': LocalizedString('logs.permissions.speak'),
            'stream': LocalizedString('logs.permissions.stream'),
            'use_application_commands': LocalizedString('logs.permissions.use_application_commands'),
            'use_embedded_activities': LocalizedString('logs.permissions.use_embedded_activities'),
            'use_external_apps': LocalizedString('logs.permissions.use_external_apps'),
            'use_external_emojis': LocalizedString('logs.permissions.use_external_emojis'),
            'use_external_sounds': LocalizedString('logs.permissions.use_external_sounds'),
            'use_external_stickers': LocalizedString('logs.permissions.use_external_stickers'),
            'use_soundboard': LocalizedString('logs.permissions.use_soundboard'),
            'use_voice_activation': LocalizedString('logs.permissions.use_voice_activation'),
            'view_audit_log': LocalizedString('logs.permissions.view_audit_log'),
            'view_channel': LocalizedString('logs.permissions.view_channel'),
            'view_creator_monetization_analytics': LocalizedString('logs.permissions.view_creator_monetization_analytics'),
            'view_guild_insights': LocalizedString('logs.permissions.view_guild_insights'),
        },
    )
    _n_logs_permissions = LogsPermissions(
        add_reaction=LocalizedString('logs.permissions.add_reaction'),
        add_reactions=LocalizedString('logs.permissions.add_reactions'),
        administrator=LocalizedString('logs.permissions.administrator'),
        attach_files=LocalizedString('logs.permissions.attach_files'),
        ban_members=LocalizedString('logs.permissions.ban_members'),
        change_nickname=LocalizedString('logs.permissions.change_nickname'),
        connect=LocalizedString('logs.permissions.connect'),
        create_events=LocalizedString('logs.permissions.create_events'),
        create_expressions=LocalizedString('logs.permissions.create_expressions'),
        create_instant_invite=LocalizedString('logs.permissions.create_instant_invite'),
        create_polls=LocalizedString('logs.permissions.create_polls'),
        create_private_threads=LocalizedString('logs.permissions.create_private_threads'),
        create_public_threads=LocalizedString('logs.permissions.create_public_threads'),
        deafen_members=LocalizedString('logs.permissions.deafen_members'),
        embed_links=LocalizedString('logs.permissions.embed_links'),
        external_emojis=LocalizedString('logs.permissions.external_emojis'),
        external_stickers=LocalizedString('logs.permissions.external_stickers'),
        kick_members=LocalizedString('logs.permissions.kick_members'),
        manage_channels=LocalizedString('logs.permissions.manage_channels'),
        manage_emojis=LocalizedString('logs.permissions.manage_emojis'),
        manage_emojis_and_stickers=LocalizedString('logs.permissions.manage_emojis_and_stickers'),
        manage_events=LocalizedString('logs.permissions.manage_events'),
        manage_expressions=LocalizedString('logs.permissions.manage_expressions'),
        manage_guild=LocalizedString('logs.permissions.manage_guild'),
        manage_messages=LocalizedString('logs.permissions.manage_messages'),
        manage_nicknames=LocalizedString('logs.permissions.manage_nicknames'),
        manage_permissions=LocalizedString('logs.permissions.manage_permissions'),
        manage_roles=LocalizedString('logs.permissions.manage_roles'),
        manage_stickers=LocalizedString('logs.permissions.manage_stickers'),
        manage_threads=LocalizedString('logs.permissions.manage_threads'),
        manage_webhooks=LocalizedString('logs.permissions.manage_webhooks'),
        mention_everyone=LocalizedString('logs.permissions.mention_everyone'),
        moderate_members=LocalizedString('logs.permissions.moderate_members'),
        move_members=LocalizedString('logs.permissions.move_members'),
        mute_members=LocalizedString('logs.permissions.mute_members'),
        priority_speaker=LocalizedString('logs.permissions.priority_speaker'),
        read_message_history=LocalizedString('logs.permissions.read_message_history'),
        read_messages=LocalizedString('logs.permissions.read_messages'),
        request_to_speak=LocalizedString('logs.permissions.request_to_speak'),
        resolve=_n_logs_permissions_resolve,
        send_messages=LocalizedString('logs.permissions.send_messages'),
        send_messages_in_threads=LocalizedString('logs.permissions.send_messages_in_threads'),
        send_polls=LocalizedString('logs.permissions.send_polls'),
        send_tts_messages=LocalizedString('logs.permissions.send_tts_messages'),
        send_voice_messages=LocalizedString('logs.permissions.send_voice_messages'),
        speak=LocalizedString('logs.permissions.speak'),
        stream=LocalizedString('logs.permissions.stream'),
        use_application_commands=LocalizedString('logs.permissions.use_application_commands'),
        use_embedded_activities=LocalizedString('logs.permissions.use_embedded_activities'),
        use_external_apps=LocalizedString('logs.permissions.use_external_apps'),
        use_external_emojis=LocalizedString('logs.permissions.use_external_emojis'),
        use_external_sounds=LocalizedString('logs.permissions.use_external_sounds'),
        use_external_stickers=LocalizedString('logs.permissions.use_external_stickers'),
        use_soundboard=LocalizedString('logs.permissions.use_soundboard'),
        use_voice_activation=LocalizedString('logs.permissions.use_voice_activation'),
        view_audit_log=LocalizedString('logs.permissions.view_audit_log'),
        view_channel=LocalizedString('logs.permissions.view_channel'),
        view_creator_monetization_analytics=LocalizedString('logs.permissions.view_creator_monetization_analytics'),
        view_guild_insights=LocalizedString('logs.permissions.view_guild_insights'),
    )
    _n_logs_presenceUpdate = LogsPresenceUpdate(
        activity=LocalizedString('logs.presenceUpdate.activity'),
        name=LocalizedString('logs.presenceUpdate.name'),
        title=LocalizedString('logs.presenceUpdate.title'),
    )
    _n_logs_reactionAdd = LogsReactionAdd(
        name=LocalizedString('logs.reactionAdd.name'),
        title=LocalizedString('logs.reactionAdd.title'),
    )
    _n_logs_reactionRemove = LogsReactionRemove(
        name=LocalizedString('logs.reactionRemove.name'),
        title=LocalizedString('logs.reactionRemove.title'),
    )
    _n_logs_remove = LogsRemove(
        description=LocalizedString('logs.remove.description'),
        name=LocalizedString('logs.remove.name'),
    )
    _n_logs_set_params_channel = LogsSetParamsChannel(
        description=LocalizedString('logs.set.params.channel.description'),
    )
    _n_logs_set_params = LogsSetParams(
        channel=_n_logs_set_params_channel,
    )
    _n_logs_set = LogsSet(
        description=LocalizedString('logs.set.description'),
        name=LocalizedString('logs.set.name'),
        params=_n_logs_set_params,
    )
    _n_logs_userUpdate_guildAvatarLocales = LogsUserUpdateGuildAvatarLocales(
        none=LocalizedString('logs.userUpdate.guildAvatarLocales.none'),
        url=LocalizedString('logs.userUpdate.guildAvatarLocales.url'),
    )
    _n_logs_userUpdate = LogsUserUpdate(
        avatar=LocalizedString('logs.userUpdate.avatar'),
        banner=LocalizedString('logs.userUpdate.banner'),
        globalName=LocalizedString('logs.userUpdate.globalName'),
        guildAvatarLocales=_n_logs_userUpdate_guildAvatarLocales,
        name=LocalizedString('logs.userUpdate.name'),
        title=LocalizedString('logs.userUpdate.title'),
        userName=LocalizedString('logs.userUpdate.userName'),
    )
    _n_logs = Logs(
        automodAction=_n_logs_automodAction,
        automodRuleCreate=_n_logs_automodRuleCreate,
        automodRuleDelete=_n_logs_automodRuleDelete,
        automodRuleUpdate=_n_logs_automodRuleUpdate,
        blacklist=_n_logs_blacklist,
        blacklistc=_n_logs_blacklistc,
        blacklistcat=_n_logs_blacklistcat,
        blacklistr=_n_logs_blacklistr,
        blacklistu=_n_logs_blacklistu,
        blacklistv=_n_logs_blacklistv,
        configure=_n_logs_configure,
        description=LocalizedString('logs.description'),
        guildChannelCreate=_n_logs_guildChannelCreate,
        guildChannelDelete=_n_logs_guildChannelDelete,
        guildChannelUpdate=_n_logs_guildChannelUpdate,
        guildRoleCreate=_n_logs_guildRoleCreate,
        guildRoleDelete=_n_logs_guildRoleDelete,
        guildRoleUpdate=_n_logs_guildRoleUpdate,
        guildUpdate=_n_logs_guildUpdate,
        guild_channelCreate=_n_logs_guild_channelCreate,
        guild_channelDelete=_n_logs_guild_channelDelete,
        guild_channelUpdate=_n_logs_guild_channelUpdate,
        inviteCreate=_n_logs_inviteCreate,
        inviteDelete=_n_logs_inviteDelete,
        memberBan=_n_logs_memberBan,
        memberJoin=_n_logs_memberJoin,
        memberRemove=_n_logs_memberRemove,
        memberUnban=_n_logs_memberUnban,
        memberUpdate=_n_logs_memberUpdate,
        messageDelete=_n_logs_messageDelete,
        messageEdit=_n_logs_messageEdit,
        name=LocalizedString('logs.name'),
        permissions=_n_logs_permissions,
        presenceUpdate=_n_logs_presenceUpdate,
        reactionAdd=_n_logs_reactionAdd,
        reactionRemove=_n_logs_reactionRemove,
        remove=_n_logs_remove,
        set=_n_logs_set,
        userUpdate=_n_logs_userUpdate,
    )
    return _n_logs


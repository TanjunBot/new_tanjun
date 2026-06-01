"""Auto-generated locale tree: commands. Do not edit."""
from __future__ import annotations

from dataclasses import dataclass

from locale_keys.types import LocalizedString, ResolveMap


@dataclass(frozen=True, slots=True)
class Commands:
    admin: CommandsAdmin
    ai: CommandsAi
    channel: CommandsChannel
    fun: CommandsFun
    games: CommandsGames
    giveaway: CommandsGiveaway
    help: CommandsHelp
    image: CommandsImage
    level: CommandsLevel
    logs: CommandsLogs
    math: CommandsMath
    utility: CommandsUtility

@dataclass(frozen=True, slots=True)
class CommandsAdmin:
    add_role: CommandsAdminAdd_role
    addrole: CommandsAdminAddrole
    administration: CommandsAdminAdministration
    ban: CommandsAdminBan
    boosterRole: CommandsAdminBoosterRole
    channel: CommandsAdminChannel
    close_ticket: CommandsAdminClose_ticket
    copy7tv: CommandsAdminCopy7tv
    copyEmoji: CommandsAdminCopyEmoji
    copyrole: CommandsAdminCopyrole
    createEmoji: CommandsAdminCreateEmoji
    create_ticket: CommandsAdminCreate_ticket
    createrole: CommandsAdminCreaterole
    database_sync: CommandsAdminDatabase_sync
    deleterole: CommandsAdminDeleterole
    demo_message: CommandsAdminDemo_message
    embed: CommandsAdminEmbed
    feedback: CommandsAdminFeedback
    joinToCreateListener: CommandsAdminJoinToCreateListener
    jointocreatechannel: CommandsAdminJointocreatechannel
    kick: CommandsAdminKick
    lock: CommandsAdminLock
    moverole: CommandsAdminMoverole
    nickname: CommandsAdminNickname
    nuke: CommandsAdminNuke
    open_ticket: CommandsAdminOpen_ticket
    purge: CommandsAdminPurge
    remove_role: CommandsAdminRemove_role
    remove_timeout: CommandsAdminRemove_timeout
    removejointocreatechannel: CommandsAdminRemovejointocreatechannel
    removerole: CommandsAdminRemoverole
    reports: CommandsAdminReports
    say: CommandsAdminSay
    setLocale: CommandsAdminSetLocale
    slowmode: CommandsAdminSlowmode
    sync: CommandsAdminSync
    timeout: CommandsAdminTimeout
    trigger_messages: CommandsAdminTrigger_messages
    unban: CommandsAdminUnban
    unlock: CommandsAdminUnlock
    update_text: CommandsAdminUpdate_text
    viewwarns: CommandsAdminViewwarns
    warn: CommandsAdminWarn
    warnconfig: CommandsAdminWarnconfig

@dataclass(frozen=True, slots=True)
class CommandsAi:
    addcustom: CommandsAiAddcustom
    approvecustom: CommandsAiApprovecustom
    ask: CommandsAiAsk
    deletecustom: CommandsAiDeletecustom
    dencustom: CommandsAiDencustom
    tokens: CommandsAiTokens

@dataclass(frozen=True, slots=True)
class CommandsChannel:
    dynamicslowmode: CommandsChannelDynamicslowmode

@dataclass(frozen=True, slots=True)
class CommandsFun:
    boop: CommandsFunBoop
    hug: CommandsFunHug
    kiss: CommandsFunKiss
    laugh: CommandsFunLaugh
    pat: CommandsFunPat
    poke: CommandsFunPoke
    slap: CommandsFunSlap
    tickle: CommandsFunTickle
    wave: CommandsFunWave

@dataclass(frozen=True, slots=True)
class CommandsGames:
    akinator: CommandsGamesAkinator
    battleship: CommandsGamesBattleship
    connect4: CommandsGamesConnect4
    flagquiz: CommandsGamesFlagquiz
    hangman: CommandsGamesHangman
    memory: CommandsGamesMemory
    rps: CommandsGamesRps
    ticTacToe: CommandsGamesTicTacToe
    tic_tac_toe: CommandsGamesTic_tac_toe
    wordle: CommandsGamesWordle

@dataclass(frozen=True, slots=True)
class CommandsGiveaway:
    add_blacklist_role: CommandsGiveawayAdd_blacklist_role
    add_blacklist_user: CommandsGiveawayAdd_blacklist_user
    builder: CommandsGiveawayBuilder
    editor: CommandsGiveawayEditor
    end_giveaway: CommandsGiveawayEnd_giveaway
    end_giveaway_command: CommandsGiveawayEnd_giveaway_command
    endedGiveaway: CommandsGiveawayEndedGiveaway
    giveawayEmbed: CommandsGiveawayGiveawayEmbed
    list_blacklist: CommandsGiveawayList_blacklist
    remove_blacklist_role: CommandsGiveawayRemove_blacklist_role
    remove_blacklist_user: CommandsGiveawayRemove_blacklist_user
    reroll_giveaway: CommandsGiveawayReroll_giveaway

@dataclass(frozen=True, slots=True)
class CommandsHelp:
    buttons: CommandsHelpButtons
    not_authorized: CommandsHelpNot_authorized
    select: CommandsHelpSelect
    timeout: CommandsHelpTimeout

@dataclass(frozen=True, slots=True)
class CommandsImage:
    background: CommandsImageBackground
    blur: CommandsImageBlur
    compress: CommandsImageCompress
    contour: CommandsImageContour
    detail: CommandsImageDetail
    edgeenhance: CommandsImageEdgeenhance
    emboss: CommandsImageEmboss
    error: CommandsImageError
    filesize: CommandsImageFilesize
    findedges: CommandsImageFindedges
    mirror: CommandsImageMirror
    rescale: CommandsImageRescale
    resize: CommandsImageResize
    sharpen: CommandsImageSharpen
    smooth: CommandsImageSmooth
    typenotsupported: CommandsImageTypenotsupported

@dataclass(frozen=True, slots=True)
class CommandsLevel:
    defaultlevelupmessage: LocalizedString
    addlevelrole: CommandsLevelAddlevelrole
    blacklist: CommandsLevelBlacklist
    boosts: CommandsLevelBoosts
    changelevelupmessage: CommandsLevelChangelevelupmessage
    changexpscaling: CommandsLevelChangexpscaling
    disablelevelsystem: CommandsLevelDisablelevelsystem
    disablelevelupmessage: CommandsLevelDisablelevelupmessage
    enablelevelsystem: CommandsLevelEnablelevelsystem
    enablelevelupmessage: CommandsLevelEnablelevelupmessage
    givexp: CommandsLevelGivexp
    leaderboard: CommandsLevelLeaderboard
    rank: CommandsLevelRank
    removelevelrole: CommandsLevelRemovelevelrole
    setbackground: CommandsLevelSetbackground
    setlevelupchannel: CommandsLevelSetlevelupchannel
    settextcooldown: CommandsLevelSettextcooldown
    setvoicecooldown: CommandsLevelSetvoicecooldown
    setxp: CommandsLevelSetxp
    showlevelroles: CommandsLevelShowlevelroles
    showxpscalings: CommandsLevelShowxpscalings
    takexp: CommandsLevelTakexp
    updateuserroles: CommandsLevelUpdateuserroles

@dataclass(frozen=True, slots=True)
class CommandsLogs:
    _text: LocalizedString
    blacklist: CommandsLogsBlacklist
    blacklistCategory: CommandsLogsBlacklistCategory
    blacklistChannel: CommandsLogsBlacklistChannel
    blacklistListCategory: CommandsLogsBlacklistListCategory
    blacklistListChannel: CommandsLogsBlacklistListChannel
    blacklistListRole: CommandsLogsBlacklistListRole
    blacklistListUser: CommandsLogsBlacklistListUser
    blacklistListVoiceChannel: CommandsLogsBlacklistListVoiceChannel
    blacklistRemoveCategory: CommandsLogsBlacklistRemoveCategory
    blacklistRemoveChannel: CommandsLogsBlacklistRemoveChannel
    blacklistRemoveRole: CommandsLogsBlacklistRemoveRole
    blacklistRemoveUser: CommandsLogsBlacklistRemoveUser
    blacklistRemoveVoiceChannel: CommandsLogsBlacklistRemoveVoiceChannel
    blacklistRole: CommandsLogsBlacklistRole
    blacklistUser: CommandsLogsBlacklistUser
    blacklistVoiceChannel: CommandsLogsBlacklistVoiceChannel
    configureLogs: CommandsLogsConfigureLogs
    removeLogChannel: CommandsLogsRemoveLogChannel
    setLogChannel: CommandsLogsSetLogChannel

@dataclass(frozen=True, slots=True)
class CommandsMath:
    calc: CommandsMathCalc
    calculator: CommandsMathCalculator
    faculty: CommandsMathFaculty
    num2word: CommandsMathNum2word
    plot_function: CommandsMathPlot_function
    plotfunction: CommandsMathPlotfunction
    randomnumber: CommandsMathRandomnumber

@dataclass(frozen=True, slots=True)
class CommandsUtility:
    afk: CommandsUtilityAfk
    autopublish: CommandsUtilityAutopublish
    avatar: CommandsUtilityAvatar
    avatarDecoration: CommandsUtilityAvatarDecoration
    banner: CommandsUtilityBanner
    boosterchannelinfo: CommandsUtilityBoosterchannelinfo
    boosterroleinfo: CommandsUtilityBoosterroleinfo
    brawlstars: CommandsUtilityBrawlstars
    claimboosterchannel: CommandsUtilityClaimboosterchannel
    claimboosterrole: CommandsUtilityClaimboosterrole
    deleteboosterchannel: CommandsUtilityDeleteboosterchannel
    deleteboosterrole: CommandsUtilityDeleteboosterrole
    feedback: CommandsUtilityFeedback
    help: CommandsUtilityHelp
    listscheduled: CommandsUtilityListscheduled
    messagetrackingoptin: CommandsUtilityMessagetrackingoptin
    messagetrackingoptout: CommandsUtilityMessagetrackingoptout
    noBanner: CommandsUtilityNoBanner
    removescheduled: CommandsUtilityRemovescheduled
    report: CommandsUtilityReport
    reports: CommandsUtilityReports
    schedulemessage: CommandsUtilitySchedulemessage
    setupboosterchannel: CommandsUtilitySetupboosterchannel
    setupboosterrole: CommandsUtilitySetupboosterrole
    twitch: CommandsUtilityTwitch

@dataclass(frozen=True, slots=True)
class CommandsAdminAdd_role:
    multipleSuccess: CommandsAdminAdd_roleMultipleSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminAddrole:
    cancelled: LocalizedString
    multiplePrompt: LocalizedString
    multipleSuccess: LocalizedString
    noSelection: LocalizedString
    alreadyHasRole: CommandsAdminAddroleAlreadyHasRole
    cancel: CommandsAdminAddroleCancel
    confirm: CommandsAdminAddroleConfirm
    managedRole: CommandsAdminAddroleManagedRole
    missingPermission: CommandsAdminAddroleMissingPermission
    missingPermissionBot: CommandsAdminAddroleMissingPermissionBot
    noRole: CommandsAdminAddroleNoRole
    noUser: CommandsAdminAddroleNoUser
    roleSelect: CommandsAdminAddroleRoleSelect
    roleTooHigh: CommandsAdminAddroleRoleTooHigh
    roleTooHighBot: CommandsAdminAddroleRoleTooHighBot
    success: CommandsAdminAddroleSuccess
    userSelect: CommandsAdminAddroleUserSelect

@dataclass(frozen=True, slots=True)
class CommandsAdminAdministration:
    bs_bot_info: LocalizedString
    bs_download_failed: LocalizedString
    bs_emoji_created: LocalizedString
    bs_emoji_failed: LocalizedString
    console_check: LocalizedString
    github_auth_test: LocalizedString
    me: LocalizedString
    permission_list: LocalizedString
    permission_result: LocalizedString
    set_guild_locale: LocalizedString
    situation_approved: LocalizedString
    situation_creator_gone: LocalizedString
    situation_deleted: LocalizedString
    situation_not_found: LocalizedString
    benchmark_bot: CommandsAdminAdministrationBenchmark_bot
    test_bot: CommandsAdminAdministrationTest_bot
    update: CommandsAdminAdministrationUpdate

@dataclass(frozen=True, slots=True)
class CommandsAdminBan:
    noReasonProvided: LocalizedString
    error: CommandsAdminBanError
    forbidden: CommandsAdminBanForbidden
    missingPermission: CommandsAdminBanMissingPermission
    missingPermissionBot: CommandsAdminBanMissingPermissionBot
    success: CommandsAdminBanSuccess
    targetTooHigh: CommandsAdminBanTargetTooHigh

@dataclass(frozen=True, slots=True)
class CommandsAdminBoosterRole:
    error: CommandsAdminBoosterRoleError
    forbidden: CommandsAdminBoosterRoleForbidden
    missingPermission: CommandsAdminBoosterRoleMissingPermission
    missingPermissionBot: CommandsAdminBoosterRoleMissingPermissionBot
    roleRemoved: CommandsAdminBoosterRoleRoleRemoved
    roleTooHighBot: CommandsAdminBoosterRoleRoleTooHighBot
    success: CommandsAdminBoosterRoleSuccess
    targetTooHigh: CommandsAdminBoosterRoleTargetTooHigh

@dataclass(frozen=True, slots=True)
class CommandsAdminChannel:
    farewell: CommandsAdminChannelFarewell
    media: CommandsAdminChannelMedia
    welcome: CommandsAdminChannelWelcome

@dataclass(frozen=True, slots=True)
class CommandsAdminClose_ticket:
    button: CommandsAdminClose_ticketButton
    error: CommandsAdminClose_ticketError
    success: CommandsAdminClose_ticketSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminCopy7tv:
    footer: LocalizedString
    noEmotes: LocalizedString
    notYourEmbed: LocalizedString
    title: LocalizedString
    addModal: CommandsAdminCopy7tvAddModal
    error: CommandsAdminCopy7tvError
    missingPermission: CommandsAdminCopy7tvMissingPermission
    missingPermissionBot: CommandsAdminCopy7tvMissingPermissionBot

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmoji:
    reason: LocalizedString
    error: CommandsAdminCopyEmojiError
    missingPermission: CommandsAdminCopyEmojiMissingPermission
    missingPermissionBot: CommandsAdminCopyEmojiMissingPermissionBot
    partialSuccess: CommandsAdminCopyEmojiPartialSuccess
    success: CommandsAdminCopyEmojiSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyrole:
    reason: LocalizedString
    missingPermission: CommandsAdminCopyroleMissingPermission
    missingPermissionBot: CommandsAdminCopyroleMissingPermissionBot
    success: CommandsAdminCopyroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateEmoji:
    allRoles: LocalizedString
    error: LocalizedString
    imageDownloadError: LocalizedString
    roleSelect: LocalizedString
    roleSelectPlaceholder: LocalizedString
    role_select: LocalizedString
    role_selectPlaceholder: LocalizedString
    missingPermission: CommandsAdminCreateEmojiMissingPermission
    success: CommandsAdminCreateEmojiSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminCreate_ticket:
    button: CommandsAdminCreate_ticketButton
    embed: CommandsAdminCreate_ticketEmbed
    error: CommandsAdminCreate_ticketError
    missingBotPermission: CommandsAdminCreate_ticketMissingBotPermission
    missingPermission: CommandsAdminCreate_ticketMissingPermission
    success: CommandsAdminCreate_ticketSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminCreaterole:
    forbidden: CommandsAdminCreateroleForbidden
    http_error: CommandsAdminCreateroleHttp_error
    iconTooLarge: CommandsAdminCreateroleIconTooLarge
    invalidColor: CommandsAdminCreateroleInvalidColor
    invalidIcon: CommandsAdminCreateroleInvalidIcon
    missingName: CommandsAdminCreateroleMissingName
    missingPermission: CommandsAdminCreateroleMissingPermission
    missingPermissionBot: CommandsAdminCreateroleMissingPermissionBot
    nameTooLong: CommandsAdminCreateroleNameTooLong
    notfound: CommandsAdminCreateroleNotfound
    reasonTooLong: CommandsAdminCreateroleReasonTooLong
    roleIconsNotEnabled: CommandsAdminCreateroleRoleIconsNotEnabled
    success: CommandsAdminCreateroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminDatabase_sync:
    aborted: LocalizedString
    analyzing: LocalizedString
    backup_error: LocalizedString
    backup_success: LocalizedString
    cancel_token: LocalizedString
    download_error: LocalizedString
    download_failed: LocalizedString
    downloading: LocalizedString
    filter_error: LocalizedString
    import_error: LocalizedString
    importing: LocalizedString
    no_attachment: LocalizedString
    no_schema_found: LocalizedString
    preparing_import: LocalizedString
    schema_prompt: LocalizedString
    schema_warning: LocalizedString
    success: LocalizedString
    timeout: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminDeleterole:
    noRole: LocalizedString
    forbidden: CommandsAdminDeleteroleForbidden
    http_error: CommandsAdminDeleteroleHttp_error
    missingPermission: CommandsAdminDeleteroleMissingPermission
    missingPermissionBot: CommandsAdminDeleteroleMissingPermissionBot
    notfound: CommandsAdminDeleteroleNotfound
    roleTooHigh: CommandsAdminDeleteroleRoleTooHigh
    roleTooHighBot: CommandsAdminDeleteroleRoleTooHighBot
    success: CommandsAdminDeleteroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminDemo_message:
    confirm: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbed:
    colorUpdated: LocalizedString
    creatorDescription: LocalizedString
    creatorTitle: LocalizedString
    descriptionUpdated: LocalizedString
    embedSent: LocalizedString
    fieldAdded: LocalizedString
    fieldEdited: LocalizedString
    fieldRemoved: LocalizedString
    footerUpdated: LocalizedString
    imageUpdated: LocalizedString
    invalidColorCode: LocalizedString
    maxFieldsReached: LocalizedString
    noFieldsToEdit: LocalizedString
    noFieldsToRemove: LocalizedString
    previewSent: LocalizedString
    thumbnailUpdated: LocalizedString
    titleUpdated: LocalizedString
    unauthorizedUser: LocalizedString
    buttons: CommandsAdminEmbedButtons
    missingPermission: CommandsAdminEmbedMissingPermission
    missingTitle: CommandsAdminEmbedMissingTitle
    modals: CommandsAdminEmbedModals
    setDescription: CommandsAdminEmbedSetDescription

@dataclass(frozen=True, slots=True)
class CommandsAdminFeedback:
    added: LocalizedString
    blocked: LocalizedString
    unblocked: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminJoinToCreateListener:
    channelDeleted: CommandsAdminJoinToCreateListenerChannelDeleted
    success: CommandsAdminJoinToCreateListenerSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminJointocreatechannel:
    alreadySet: CommandsAdminJointocreatechannelAlreadySet
    missingPermission: CommandsAdminJointocreatechannelMissingPermission
    success: CommandsAdminJointocreatechannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminKick:
    noReasonProvided: LocalizedString
    error: CommandsAdminKickError
    forbidden: CommandsAdminKickForbidden
    missingPermission: CommandsAdminKickMissingPermission
    missingPermissionBot: CommandsAdminKickMissingPermissionBot
    success: CommandsAdminKickSuccess
    targetTooHigh: CommandsAdminKickTargetTooHigh

@dataclass(frozen=True, slots=True)
class CommandsAdminLock:
    channelLockedMessage: LocalizedString
    alreadyLocked: CommandsAdminLockAlreadyLocked
    error: CommandsAdminLockError
    forbidden: CommandsAdminLockForbidden
    missingPermission: CommandsAdminLockMissingPermission
    missingPermissionBot: CommandsAdminLockMissingPermissionBot
    success: CommandsAdminLockSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminMoverole:
    error: CommandsAdminMoveroleError
    forbidden: CommandsAdminMoveroleForbidden
    missingPermission: CommandsAdminMoveroleMissingPermission
    missingPermissionBot: CommandsAdminMoveroleMissingPermissionBot
    roleTooHigh: CommandsAdminMoveroleRoleTooHigh
    success: CommandsAdminMoveroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminNickname:
    changed: CommandsAdminNicknameChanged
    error: CommandsAdminNicknameError
    forbidden: CommandsAdminNicknameForbidden
    missingPermission: CommandsAdminNicknameMissingPermission
    missingPermissionBot: CommandsAdminNicknameMissingPermissionBot
    removed: CommandsAdminNicknameRemoved
    targetTooHigh: CommandsAdminNicknameTargetTooHigh

@dataclass(frozen=True, slots=True)
class CommandsAdminNuke:
    cancel: LocalizedString
    cancelledMessage: LocalizedString
    confirm: LocalizedString
    confirmationDescription: LocalizedString
    confirmationPrompt: LocalizedString
    confirmationTitle: LocalizedString
    confirmationWord: LocalizedString
    forbiddenError: LocalizedString
    httpError: LocalizedString
    incorrectConfirmation: LocalizedString
    nukeReason: LocalizedString
    nukeSuccessMessage: LocalizedString
    timeoutMessage: LocalizedString
    unauthorizedUser: LocalizedString
    missingPermission: CommandsAdminNukeMissingPermission
    missingPermissionBot: CommandsAdminNukeMissingPermissionBot
    notfound: CommandsAdminNukeNotfound

@dataclass(frozen=True, slots=True)
class CommandsAdminOpen_ticket:
    error: CommandsAdminOpen_ticketError
    optedOutWarning: CommandsAdminOpen_ticketOptedOutWarning
    success: CommandsAdminOpen_ticketSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminPurge:
    error: CommandsAdminPurgeError
    forbidden: CommandsAdminPurgeForbidden
    invalidAmount: CommandsAdminPurgeInvalidAmount
    missingPermission: CommandsAdminPurgeMissingPermission
    missingPermissionBot: CommandsAdminPurgeMissingPermissionBot
    success: CommandsAdminPurgeSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_role:
    multipleSuccess: CommandsAdminRemove_roleMultipleSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_timeout:
    noReasonProvided: LocalizedString
    error: CommandsAdminRemove_timeoutError
    forbidden: CommandsAdminRemove_timeoutForbidden
    missingPermission: CommandsAdminRemove_timeoutMissingPermission
    missingPermissionBot: CommandsAdminRemove_timeoutMissingPermissionBot
    notTimedOut: CommandsAdminRemove_timeoutNotTimedOut
    success: CommandsAdminRemove_timeoutSuccess
    targetTooHigh: CommandsAdminRemove_timeoutTargetTooHigh

@dataclass(frozen=True, slots=True)
class CommandsAdminRemovejointocreatechannel:
    alreadySet: CommandsAdminRemovejointocreatechannelAlreadySet
    missingPermission: CommandsAdminRemovejointocreatechannelMissingPermission
    notSet: CommandsAdminRemovejointocreatechannelNotSet
    success: CommandsAdminRemovejointocreatechannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoverole:
    cancelled: LocalizedString
    error: LocalizedString
    multiplePrompt: LocalizedString
    multipleSuccess: LocalizedString
    noSelection: LocalizedString
    selectRoles: LocalizedString
    selectUsers: LocalizedString
    cancel: CommandsAdminRemoveroleCancel
    confirm: CommandsAdminRemoveroleConfirm
    doesNotHaveRole: CommandsAdminRemoveroleDoesNotHaveRole
    managedRole: CommandsAdminRemoveroleManagedRole
    missingPermission: CommandsAdminRemoveroleMissingPermission
    missingPermissionBot: CommandsAdminRemoveroleMissingPermissionBot
    noRole: CommandsAdminRemoveroleNoRole
    noUser: CommandsAdminRemoveroleNoUser
    roleTooHigh: CommandsAdminRemoveroleRoleTooHigh
    roleTooHighBot: CommandsAdminRemoveroleRoleTooHighBot
    success: CommandsAdminRemoveroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminReports:
    remove_channel: CommandsAdminReportsRemove_channel
    set_channel: CommandsAdminReportsSet_channel
    show_reports: CommandsAdminReportsShow_reports
    unblock_reporter: CommandsAdminReportsUnblock_reporter

@dataclass(frozen=True, slots=True)
class CommandsAdminSay:
    error: CommandsAdminSayError
    missingPermission: CommandsAdminSayMissingPermission
    missingPermissionBot: CommandsAdminSayMissingPermissionBot
    success: CommandsAdminSaySuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminSetLocale:
    setLocaleReason: LocalizedString
    missingPermission: CommandsAdminSetLocaleMissingPermission
    success: CommandsAdminSetLocaleSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminSlowmode:
    disabled: CommandsAdminSlowmodeDisabled
    enabled: CommandsAdminSlowmodeEnabled
    error: CommandsAdminSlowmodeError
    forbidden: CommandsAdminSlowmodeForbidden
    invalidDuration: CommandsAdminSlowmodeInvalidDuration
    missingPermission: CommandsAdminSlowmodeMissingPermission
    missingPermissionBot: CommandsAdminSlowmodeMissingPermissionBot

@dataclass(frozen=True, slots=True)
class CommandsAdminSync:
    completed: LocalizedString
    failed: LocalizedString
    in_progress: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTimeout:
    noReasonProvided: LocalizedString
    alreadyTimedOut: CommandsAdminTimeoutAlreadyTimedOut
    error: CommandsAdminTimeoutError
    forbidden: CommandsAdminTimeoutForbidden
    invalidDuration: CommandsAdminTimeoutInvalidDuration
    missingPermission: CommandsAdminTimeoutMissingPermission
    missingPermissionBot: CommandsAdminTimeoutMissingPermissionBot
    success: CommandsAdminTimeoutSuccess
    targetTooHigh: CommandsAdminTimeoutTargetTooHigh

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messages:
    add: CommandsAdminTrigger_messagesAdd
    configure: CommandsAdminTrigger_messagesConfigure

@dataclass(frozen=True, slots=True)
class CommandsAdminUnban:
    noReasonProvided: LocalizedString
    error: CommandsAdminUnbanError
    forbidden: CommandsAdminUnbanForbidden
    missingPermission: CommandsAdminUnbanMissingPermission
    missingPermissionBot: CommandsAdminUnbanMissingPermissionBot
    success: CommandsAdminUnbanSuccess
    userNotFound: CommandsAdminUnbanUserNotFound

@dataclass(frozen=True, slots=True)
class CommandsAdminUnlock:
    channelUnlockedMessage: LocalizedString
    error: CommandsAdminUnlockError
    forbidden: CommandsAdminUnlockForbidden
    missingPermission: CommandsAdminUnlockMissingPermission
    missingPermissionBot: CommandsAdminUnlockMissingPermissionBot
    notLocked: CommandsAdminUnlockNotLocked
    success: CommandsAdminUnlockSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminUpdate_text:
    cancelled: LocalizedString
    confirm: LocalizedString
    confirm2: LocalizedString
    enter_password: LocalizedString
    expected_password: LocalizedString
    say_wallah: LocalizedString
    timeout: LocalizedString
    wrong_password: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminViewwarns:
    description: LocalizedString
    never: LocalizedString
    nextButton: LocalizedString
    noReason: LocalizedString
    pageFooter: LocalizedString
    prevButton: LocalizedString
    removeButton: LocalizedString
    title: LocalizedString
    unauthorizedUser: LocalizedString
    warningDetails: LocalizedString
    warningEntry: LocalizedString
    missingPermission: CommandsAdminViewwarnsMissingPermission
    noWarnings: CommandsAdminViewwarnsNoWarnings

@dataclass(frozen=True, slots=True)
class CommandsAdminWarn:
    noReasonProvided: LocalizedString
    dmNotification: CommandsAdminWarnDmNotification
    missingPermission: CommandsAdminWarnMissingPermission
    reason: CommandsAdminWarnReason
    success: CommandsAdminWarnSuccess
    targetTooHigh: CommandsAdminWarnTargetTooHigh

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfig:
    currentConfig: CommandsAdminWarnconfigCurrentConfig
    error: CommandsAdminWarnconfigError
    missingPermission: CommandsAdminWarnconfigMissingPermission
    modal: CommandsAdminWarnconfigModal
    success: CommandsAdminWarnconfigSuccess

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustom:
    alreadyexists: CommandsAiAddcustomAlreadyexists
    invalidfrequency_penalty: CommandsAiAddcustomInvalidfrequency_penalty
    invalidpresence_penalty: CommandsAiAddcustomInvalidpresence_penalty
    invalidtemperature: CommandsAiAddcustomInvalidtemperature
    invalidtop_p: CommandsAiAddcustomInvalidtop_p
    longname: CommandsAiAddcustomLongname
    longsituation: CommandsAiAddcustomLongsituation
    namealreadyexists: CommandsAiAddcustomNamealreadyexists
    notplus: CommandsAiAddcustomNotplus
    shortname: CommandsAiAddcustomShortname
    shortsituation: CommandsAiAddcustomShortsituation
    success: CommandsAiAddcustomSuccess

@dataclass(frozen=True, slots=True)
class CommandsAiApprovecustom:
    success: CommandsAiApprovecustomSuccess

@dataclass(frozen=True, slots=True)
class CommandsAiAsk:
    error: CommandsAiAskError
    noapi: CommandsAiAskNoapi
    notoken: CommandsAiAskNotoken
    success: CommandsAiAskSuccess

@dataclass(frozen=True, slots=True)
class CommandsAiTokens:
    success: CommandsAiTokensSuccess

@dataclass(frozen=True, slots=True)
class CommandsAiDeletecustom:
    notfound: CommandsAiDeletecustomNotfound
    success: CommandsAiDeletecustomSuccess

@dataclass(frozen=True, slots=True)
class CommandsAiDencustom:
    success: CommandsAiDencustomSuccess

@dataclass(frozen=True, slots=True)
class CommandsChannelDynamicslowmode:
    reason: LocalizedString
    resetReason: LocalizedString
    alreadySet: CommandsChannelDynamicslowmodeAlreadySet
    channels: CommandsChannelDynamicslowmodeChannels
    deleteSuccess: CommandsChannelDynamicslowmodeDeleteSuccess
    missingBotPermission: CommandsChannelDynamicslowmodeMissingBotPermission
    missingPermission: CommandsChannelDynamicslowmodeMissingPermission
    noChannels: CommandsChannelDynamicslowmodeNoChannels
    notSet: CommandsChannelDynamicslowmodeNotSet
    success: CommandsChannelDynamicslowmodeSuccess

@dataclass(frozen=True, slots=True)
class CommandsFunBoop:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsFunHug:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsFunKiss:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsFunLaugh:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsFunPat:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsFunPoke:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsFunSlap:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsFunTickle:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsFunWave:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesBattleship:
    alreadyAttacked: LocalizedString
    battleTitle: LocalizedString
    currentTurn: LocalizedString
    gameOver: LocalizedString
    helpAttackInstruction: LocalizedString
    helpBoards: LocalizedString
    helpCurrentTurn: LocalizedString
    helpEnemyBoard: LocalizedString
    helpGiveUp: LocalizedString
    helpGiveUpInstruction: LocalizedString
    helpPlayers: LocalizedString
    helpPlayersValue: LocalizedString
    helpTitle: LocalizedString
    helpToAttack: LocalizedString
    helpYourBoard: LocalizedString
    legend: LocalizedString
    notYourGame: LocalizedString
    notYourTurn: LocalizedString
    placementDescription: LocalizedString
    placementTitle: LocalizedString
    winner: LocalizedString
    error: CommandsGamesBattleshipError

@dataclass(frozen=True, slots=True)
class CommandsGamesConnect4:
    cellAlreadyTaken: LocalizedString
    currentTurn: LocalizedString
    description: LocalizedString
    descriptionBotEnemy: LocalizedString
    draw: LocalizedString
    drop: LocalizedString
    invalidMove: LocalizedString
    notYourGame: LocalizedString
    notYourTurn: LocalizedString
    title: LocalizedString
    winner: LocalizedString
    error: CommandsGamesConnect4Error

@dataclass(frozen=True, slots=True)
class CommandsGamesFlagquiz:
    description: LocalizedString
    hint: LocalizedString
    notYourGame: LocalizedString
    title: LocalizedString
    buttons: CommandsGamesFlagquizButtons
    error: CommandsGamesFlagquizError
    failure: CommandsGamesFlagquizFailure
    givenUp: CommandsGamesFlagquizGivenUp
    initial: CommandsGamesFlagquizInitial
    modal: CommandsGamesFlagquizModal
    success: CommandsGamesFlagquizSuccess

@dataclass(frozen=True, slots=True)
class CommandsGamesHangman:
    description: LocalizedString
    notYourGame: LocalizedString
    title: LocalizedString
    buttons: CommandsGamesHangmanButtons
    error: CommandsGamesHangmanError
    failure: CommandsGamesHangmanFailure
    givenUp: CommandsGamesHangmanGivenUp
    initial: CommandsGamesHangmanInitial
    modal: CommandsGamesHangmanModal
    success: CommandsGamesHangmanSuccess
    wrongGuess: CommandsGamesHangmanWrongGuess

@dataclass(frozen=True, slots=True)
class CommandsGamesWordle:
    description: LocalizedString
    notYourGame: LocalizedString
    title: LocalizedString
    buttons: CommandsGamesWordleButtons
    error: CommandsGamesWordleError
    failure: CommandsGamesWordleFailure
    givenUp: CommandsGamesWordleGivenUp
    hardMode: CommandsGamesWordleHardMode
    initial: CommandsGamesWordleInitial
    modal: CommandsGamesWordleModal
    pickMode: CommandsGamesWordlePickMode
    stats: CommandsGamesWordleStats
    success: CommandsGamesWordleSuccess

@dataclass(frozen=True, slots=True)
class CommandsGamesAkinator:
    back: LocalizedString
    description: LocalizedString
    end: LocalizedString
    idk: LocalizedString
    no: LocalizedString
    no_answer: LocalizedString
    notYourGame: LocalizedString
    probably: LocalizedString
    probably_not: LocalizedString
    result: LocalizedString
    title: LocalizedString
    yes: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesMemory:
    game_over: LocalizedString
    match: LocalizedString
    no_match: LocalizedString
    not_your_game: LocalizedString
    pairs_found: LocalizedString
    player: LocalizedString
    rules_intro: LocalizedString
    select_first: LocalizedString
    select_second: LocalizedString
    title: LocalizedString
    turns: LocalizedString
    win: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesRps:
    description: LocalizedString
    draw: LocalizedString
    drawDescription: LocalizedString
    lose: LocalizedString
    loseDescription: LocalizedString
    notYourGame: LocalizedString
    paper: LocalizedString
    rock: LocalizedString
    scissors: LocalizedString
    title: LocalizedString
    win: LocalizedString
    winDescription: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesTicTacToe:
    cellAlreadyTaken: LocalizedString
    currentTurn: LocalizedString
    description: LocalizedString
    descriptionBotEnemy: LocalizedString
    draw: LocalizedString
    invalidMove: LocalizedString
    notYourGame: LocalizedString
    notYourTurn: LocalizedString
    title: LocalizedString
    winner: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesTic_tac_toe:
    cellAlreadyTaken: LocalizedString
    currentTurn: LocalizedString
    description: LocalizedString
    descriptionBotEnemy: LocalizedString
    draw: LocalizedString
    invalidMove: LocalizedString
    notYourGame: LocalizedString
    notYourTurn: LocalizedString
    title: LocalizedString
    winner: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayAdd_blacklist_role:
    alreadyBlacklisted: CommandsGiveawayAdd_blacklist_roleAlreadyBlacklisted
    missingPermission: CommandsGiveawayAdd_blacklist_roleMissingPermission
    pro_required: CommandsGiveawayAdd_blacklist_rolePro_required
    success: CommandsGiveawayAdd_blacklist_roleSuccess

@dataclass(frozen=True, slots=True)
class CommandsGiveawayAdd_blacklist_user:
    alreadyBlacklisted: CommandsGiveawayAdd_blacklist_userAlreadyBlacklisted
    missingPermission: CommandsGiveawayAdd_blacklist_userMissingPermission
    success: CommandsGiveawayAdd_blacklist_userSuccess

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilder:
    cancel: LocalizedString
    change_description: LocalizedString
    channel_selected: LocalizedString
    confirm: LocalizedString
    enter_description: LocalizedString
    enter_message: LocalizedString
    enter_price: LocalizedString
    false: LocalizedString
    loading: LocalizedString
    no_permission: LocalizedString
    none: LocalizedString
    not_authorized: LocalizedString
    preview: LocalizedString
    true: LocalizedString
    winners: LocalizedString
    with_button: LocalizedString
    add_channel_requirement: CommandsGiveawayBuilderAdd_channel_requirement
    change_winners: CommandsGiveawayBuilderChange_winners
    channel: CommandsGiveawayBuilderChannel
    custom_name: CommandsGiveawayBuilderCustom_name
    day_requirement: CommandsGiveawayBuilderDay_requirement
    description: CommandsGiveawayBuilderDescription
    end_time: CommandsGiveawayBuilderEnd_time
    message: CommandsGiveawayBuilderMessage
    modal: CommandsGiveawayBuilderModal
    new_message_requirement: CommandsGiveawayBuilderNew_message_requirement
    price: CommandsGiveawayBuilderPrice
    remove_channel_requirement: CommandsGiveawayBuilderRemove_channel_requirement
    role_requirement: CommandsGiveawayBuilderRole_requirement
    sponsor: CommandsGiveawayBuilderSponsor
    start_time: CommandsGiveawayBuilderStart_time
    success: CommandsGiveawayBuilderSuccess
    voice_requirement: CommandsGiveawayBuilderVoice_requirement
    winner: CommandsGiveawayBuilderWinner

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEditor:
    loading: LocalizedString
    no_permission: LocalizedString
    not_authorized: LocalizedString
    not_found: LocalizedString
    pro_required: LocalizedString
    success: CommandsGiveawayEditorSuccess

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveaway:
    deleted: CommandsGiveawayEnd_giveawayDeleted
    error: CommandsGiveawayEnd_giveawayError
    success: CommandsGiveawayEnd_giveawaySuccess

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveaway_command:
    deleted: CommandsGiveawayEnd_giveaway_commandDeleted
    error: CommandsGiveawayEnd_giveaway_commandError
    success: CommandsGiveawayEnd_giveaway_commandSuccess

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEndedGiveaway:
    button_text: LocalizedString
    description: LocalizedString
    dm: LocalizedString
    title: LocalizedString
    winnerDM: LocalizedString
    no_participants: CommandsGiveawayEndedGiveawayNo_participants

@dataclass(frozen=True, slots=True)
class CommandsGiveawayGiveawayEmbed:
    button_text: LocalizedString
    channel_requirements: LocalizedString
    day_requirement: LocalizedString
    description: LocalizedString
    end_time: LocalizedString
    footer: LocalizedString
    new_message_requirement: LocalizedString
    no_requirements: LocalizedString
    price: LocalizedString
    role_requirement: LocalizedString
    sponsor: LocalizedString
    title: LocalizedString
    voice_requirement: LocalizedString
    participation_failed: CommandsGiveawayGiveawayEmbedParticipation_failed
    participation_removed: CommandsGiveawayGiveawayEmbedParticipation_removed
    participation_success: CommandsGiveawayGiveawayEmbedParticipation_success

@dataclass(frozen=True, slots=True)
class CommandsGiveawayList_blacklist:
    description: LocalizedString
    empty: LocalizedString
    roles: LocalizedString
    title: LocalizedString
    users: LocalizedString
    missingPermission: CommandsGiveawayList_blacklistMissingPermission
    noBlacklist: CommandsGiveawayList_blacklistNoBlacklist

@dataclass(frozen=True, slots=True)
class CommandsGiveawayRemove_blacklist_role:
    missingPermission: CommandsGiveawayRemove_blacklist_roleMissingPermission
    notBlacklisted: CommandsGiveawayRemove_blacklist_roleNotBlacklisted
    success: CommandsGiveawayRemove_blacklist_roleSuccess

@dataclass(frozen=True, slots=True)
class CommandsGiveawayRemove_blacklist_user:
    missingPermission: CommandsGiveawayRemove_blacklist_userMissingPermission
    notBlacklisted: CommandsGiveawayRemove_blacklist_userNotBlacklisted
    success: CommandsGiveawayRemove_blacklist_userSuccess

@dataclass(frozen=True, slots=True)
class CommandsGiveawayReroll_giveaway:
    rerollAllWinners: LocalizedString
    rerollOneWinner: LocalizedString
    winnerDM: LocalizedString
    error: CommandsGiveawayReroll_giveawayError
    selectOption: CommandsGiveawayReroll_giveawaySelectOption
    success: CommandsGiveawayReroll_giveawaySuccess

@dataclass(frozen=True, slots=True)
class CommandsHelpButtons:
    next: LocalizedString
    previous: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsHelpNot_authorized:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsHelpSelect:
    description: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsHelpTimeout:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageBackground:
    disabled: CommandsImageBackgroundDisabled
    success: CommandsImageBackgroundSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageBlur:
    success: CommandsImageBlurSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageCompress:
    success: CommandsImageCompressSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageContour:
    success: CommandsImageContourSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageDetail:
    success: CommandsImageDetailSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageEdgeenhance:
    success: CommandsImageEdgeenhanceSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageEmboss:
    success: CommandsImageEmbossSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageError:
    unknown_filter: CommandsImageErrorUnknown_filter

@dataclass(frozen=True, slots=True)
class CommandsImageFindedges:
    success: CommandsImageFindedgesSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageMirror:
    invalidaxis: CommandsImageMirrorInvalidaxis
    success: CommandsImageMirrorSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageRescale:
    success: CommandsImageRescaleSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageResize:
    success: CommandsImageResizeSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageSharpen:
    success: CommandsImageSharpenSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageSmooth:
    success: CommandsImageSmoothSuccess

@dataclass(frozen=True, slots=True)
class CommandsImageFilesize:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageTypenotsupported:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelAddlevelrole:
    error: CommandsLevelAddlevelroleError
    success: CommandsLevelAddlevelroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklist:
    no_reason: LocalizedString
    add_channel: CommandsLevelBlacklistAdd_channel
    add_role: CommandsLevelBlacklistAdd_role
    add_user: CommandsLevelBlacklistAdd_user
    remove_channel: CommandsLevelBlacklistRemove_channel
    remove_role: CommandsLevelBlacklistRemove_role
    remove_user: CommandsLevelBlacklistRemove_user
    show: CommandsLevelBlacklistShow

@dataclass(frozen=True, slots=True)
class CommandsLevelBoosts:
    additive: LocalizedString
    multiplicative: LocalizedString
    add_channel: CommandsLevelBoostsAdd_channel
    add_role: CommandsLevelBoostsAdd_role
    add_user: CommandsLevelBoostsAdd_user
    calculate_user_channel: CommandsLevelBoostsCalculate_user_channel
    error: CommandsLevelBoostsError
    remove_channel: CommandsLevelBoostsRemove_channel
    remove_role: CommandsLevelBoostsRemove_role
    remove_user: CommandsLevelBoostsRemove_user
    show: CommandsLevelBoostsShow

@dataclass(frozen=True, slots=True)
class CommandsLevelChangelevelupmessage:
    error: CommandsLevelChangelevelupmessageError
    success: CommandsLevelChangelevelupmessageSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelChangexpscaling:
    xp_examples: LocalizedString
    error: CommandsLevelChangexpscalingError
    formulas: CommandsLevelChangexpscalingFormulas
    scalings: CommandsLevelChangexpscalingScalings
    success: CommandsLevelChangexpscalingSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelsystem:
    cancel: LocalizedString
    confirm: LocalizedString
    description: LocalizedString
    name: LocalizedString
    cancel: CommandsLevelDisablelevelsystemCancel
    confirmation: CommandsLevelDisablelevelsystemConfirmation
    error: CommandsLevelDisablelevelsystemError
    success: CommandsLevelDisablelevelsystemSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelupmessage:
    error: CommandsLevelDisablelevelupmessageError
    success: CommandsLevelDisablelevelupmessageSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelsystem:
    description: LocalizedString
    name: LocalizedString
    error: CommandsLevelEnablelevelsystemError
    success: CommandsLevelEnablelevelsystemSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelupmessage:
    error: CommandsLevelEnablelevelupmessageError
    success: CommandsLevelEnablelevelupmessageSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelGivexp:
    error: CommandsLevelGivexpError
    success: CommandsLevelGivexpSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelRank:
    data: CommandsLevelRankData
    error: CommandsLevelRankError
    success: CommandsLevelRankSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelRemovelevelrole:
    error: CommandsLevelRemovelevelroleError
    success: CommandsLevelRemovelevelroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelSetbackground:
    error: CommandsLevelSetbackgroundError
    success: CommandsLevelSetbackgroundSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelSetlevelupchannel:
    error: CommandsLevelSetlevelupchannelError
    reset: CommandsLevelSetlevelupchannelReset
    success: CommandsLevelSetlevelupchannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelSettextcooldown:
    description: LocalizedString
    name: LocalizedString
    error: CommandsLevelSettextcooldownError
    params: CommandsLevelSettextcooldownParams
    success: CommandsLevelSettextcooldownSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelSetvoicecooldown:
    description: LocalizedString
    name: LocalizedString
    error: CommandsLevelSetvoicecooldownError
    params: CommandsLevelSetvoicecooldownParams
    success: CommandsLevelSetvoicecooldownSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelSetxp:
    error: CommandsLevelSetxpError
    success: CommandsLevelSetxpSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelShowlevelroles:
    add_button: LocalizedString
    add_role_cancelled: LocalizedString
    add_role_prompt: LocalizedString
    cancel_button: LocalizedString
    data: LocalizedString
    description: LocalizedString
    level: LocalizedString
    next_button: LocalizedString
    previous_button: LocalizedString
    remove_button: LocalizedString
    remove_role_cancelled: LocalizedString
    remove_role_confirm: LocalizedString
    remove_role_data: LocalizedString
    remove_role_prompt: LocalizedString
    remove_role_select_placeholder: LocalizedString
    remove_role_success: LocalizedString
    role_select_placeholder: LocalizedString
    select_placeholder: LocalizedString
    title: LocalizedString
    add_role_modal: CommandsLevelShowlevelrolesAdd_role_modal
    error: CommandsLevelShowlevelrolesError
    no_roles: CommandsLevelShowlevelrolesNo_roles
    remove_role_confirm: CommandsLevelShowlevelrolesRemove_role_confirm
    selected_level: CommandsLevelShowlevelrolesSelected_level

@dataclass(frozen=True, slots=True)
class CommandsLevelTakexp:
    error: CommandsLevelTakexpError
    success: CommandsLevelTakexpSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelUpdateuserroles:
    reason: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelLeaderboard:
    data: LocalizedString
    next: LocalizedString
    no_data: LocalizedString
    notYourEmbed: LocalizedString
    page: LocalizedString
    previous: LocalizedString
    title: LocalizedString
    titleNoPages: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelShowxpscalings:
    data: LocalizedString
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklist:
    description: LocalizedString
    name: LocalizedString
    add: CommandsLogsBlacklistAdd
    remove: CommandsLogsBlacklistRemove
    show: CommandsLogsBlacklistShow

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistCategory:
    alreadyBlacklisted: CommandsLogsBlacklistCategoryAlreadyBlacklisted
    blacklisted: CommandsLogsBlacklistCategoryBlacklisted
    missingChannel: CommandsLogsBlacklistCategoryMissingChannel
    missingPermission: CommandsLogsBlacklistCategoryMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistChannel:
    alreadyBlacklisted: CommandsLogsBlacklistChannelAlreadyBlacklisted
    blacklisted: CommandsLogsBlacklistChannelBlacklisted
    missingPermission: CommandsLogsBlacklistChannelMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListCategory:
    noBlacklistedCategories: LocalizedString
    title: LocalizedString
    addCategory: CommandsLogsBlacklistListCategoryAddCategory
    missingPermission: CommandsLogsBlacklistListCategoryMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListChannel:
    noBlacklistedChannels: LocalizedString
    title: LocalizedString
    addChannel: CommandsLogsBlacklistListChannelAddChannel
    missingPermission: CommandsLogsBlacklistListChannelMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListRole:
    noBlacklistedRoles: LocalizedString
    title: LocalizedString
    addRole: CommandsLogsBlacklistListRoleAddRole
    missingPermission: CommandsLogsBlacklistListRoleMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListUser:
    noBlacklistedUsers: LocalizedString
    title: LocalizedString
    addUser: CommandsLogsBlacklistListUserAddUser
    missingPermission: CommandsLogsBlacklistListUserMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListVoiceChannel:
    noBlacklistedChannels: LocalizedString
    title: LocalizedString
    addChannel: CommandsLogsBlacklistListVoiceChannelAddChannel
    missingPermission: CommandsLogsBlacklistListVoiceChannelMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveCategory:
    missingChannel: CommandsLogsBlacklistRemoveCategoryMissingChannel
    missingPermission: CommandsLogsBlacklistRemoveCategoryMissingPermission
    notBlacklisted: CommandsLogsBlacklistRemoveCategoryNotBlacklisted
    success: CommandsLogsBlacklistRemoveCategorySuccess

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveChannel:
    missingPermission: CommandsLogsBlacklistRemoveChannelMissingPermission
    notBlacklisted: CommandsLogsBlacklistRemoveChannelNotBlacklisted
    success: CommandsLogsBlacklistRemoveChannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveRole:
    missingPermission: CommandsLogsBlacklistRemoveRoleMissingPermission
    notBlacklisted: CommandsLogsBlacklistRemoveRoleNotBlacklisted
    success: CommandsLogsBlacklistRemoveRoleSuccess

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveUser:
    missingPermission: CommandsLogsBlacklistRemoveUserMissingPermission
    notBlacklisted: CommandsLogsBlacklistRemoveUserNotBlacklisted
    success: CommandsLogsBlacklistRemoveUserSuccess

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveVoiceChannel:
    missingChannel: CommandsLogsBlacklistRemoveVoiceChannelMissingChannel
    missingPermission: CommandsLogsBlacklistRemoveVoiceChannelMissingPermission
    notBlacklisted: CommandsLogsBlacklistRemoveVoiceChannelNotBlacklisted
    success: CommandsLogsBlacklistRemoveVoiceChannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRole:
    alreadyBlacklisted: CommandsLogsBlacklistRoleAlreadyBlacklisted
    blacklisted: CommandsLogsBlacklistRoleBlacklisted
    missingPermission: CommandsLogsBlacklistRoleMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistUser:
    alreadyBlacklisted: CommandsLogsBlacklistUserAlreadyBlacklisted
    blacklisted: CommandsLogsBlacklistUserBlacklisted
    missingPermission: CommandsLogsBlacklistUserMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistVoiceChannel:
    alreadyBlacklisted: CommandsLogsBlacklistVoiceChannelAlreadyBlacklisted
    blacklisted: CommandsLogsBlacklistVoiceChannelBlacklisted
    missingChannel: CommandsLogsBlacklistVoiceChannelMissingChannel
    missingPermission: CommandsLogsBlacklistVoiceChannelMissingPermission

@dataclass(frozen=True, slots=True)
class CommandsLogsConfigureLogs:
    title: LocalizedString
    configurationEmbed: CommandsLogsConfigureLogsConfigurationEmbed
    configuration_embed: CommandsLogsConfigureLogsConfiguration_embed
    noLogEnabled: CommandsLogsConfigureLogsNoLogEnabled

@dataclass(frozen=True, slots=True)
class CommandsLogsRemoveLogChannel:
    missingPermission: CommandsLogsRemoveLogChannelMissingPermission
    notSet: CommandsLogsRemoveLogChannelNotSet
    success: CommandsLogsRemoveLogChannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsLogsSetLogChannel:
    alreadySet: CommandsLogsSetLogChannelAlreadySet
    botMissingPermission: CommandsLogsSetLogChannelBotMissingPermission
    missingPermission: CommandsLogsSetLogChannelMissingPermission
    success: CommandsLogsSetLogChannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsMathCalc:
    error: CommandsMathCalcError
    success: CommandsMathCalcSuccess

@dataclass(frozen=True, slots=True)
class CommandsMathFaculty:
    error: CommandsMathFacultyError
    success: CommandsMathFacultySuccess

@dataclass(frozen=True, slots=True)
class CommandsMathNum2word:
    description: LocalizedString
    title: LocalizedString
    locales: CommandsMathNum2wordLocales

@dataclass(frozen=True, slots=True)
class CommandsMathPlot_function:
    error: LocalizedString
    no_functions_to_rename: LocalizedString
    not_clickable: LocalizedString
    unexpected_error: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunction:
    default_title: LocalizedString
    default_x_label: LocalizedString
    default_y_label: LocalizedString
    description: LocalizedString
    error: LocalizedString
    extrema: LocalizedString
    extremum: LocalizedString
    inflection: LocalizedString
    inflection_points: LocalizedString
    no_functions_to_rename: LocalizedString
    not_clickable: LocalizedString
    plot_title: LocalizedString
    unexpected_error: LocalizedString
    x_axis: LocalizedString
    y_axis: LocalizedString
    zero: LocalizedString
    zeros: LocalizedString
    buttons: CommandsMathPlotfunctionButtons
    error: CommandsMathPlotfunctionError
    messages: CommandsMathPlotfunctionMessages
    modals: CommandsMathPlotfunctionModals
    select_menus: CommandsMathPlotfunctionSelect_menus

@dataclass(frozen=True, slots=True)
class CommandsMathRandomnumber:
    not_truly_random: LocalizedString
    error: CommandsMathRandomnumberError
    success: CommandsMathRandomnumberSuccess

@dataclass(frozen=True, slots=True)
class CommandsMathCalculator:
    command_description: LocalizedString
    command_name: LocalizedString
    equation: LocalizedString
    error: LocalizedString
    history: LocalizedString
    invalid_assignment: LocalizedString
    result: LocalizedString
    title: LocalizedString
    unauthorizedUser: LocalizedString
    variables: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAfk:
    already_afk: CommandsUtilityAfkAlready_afk
    mentions: CommandsUtilityAfkMentions
    mentions_one: CommandsUtilityAfkMentions_one
    opted_out: CommandsUtilityAfkOpted_out
    removed: CommandsUtilityAfkRemoved
    removed_no_messages: CommandsUtilityAfkRemoved_no_messages
    success: CommandsUtilityAfkSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityAutopublish:
    error: CommandsUtilityAutopublishError
    remove_success: CommandsUtilityAutopublishRemove_success
    success: CommandsUtilityAutopublishSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityAvatarDecoration:
    description: LocalizedString
    title: LocalizedString
    no_decoration: CommandsUtilityAvatarDecorationNo_decoration

@dataclass(frozen=True, slots=True)
class CommandsUtilityBoosterchannelinfo:
    info: CommandsUtilityBoosterchannelinfoInfo

@dataclass(frozen=True, slots=True)
class CommandsUtilityBoosterroleinfo:
    info: CommandsUtilityBoosterroleinfoInfo

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstars:
    battlelog: CommandsUtilityBrawlstarsBattlelog
    brawlers: CommandsUtilityBrawlstarsBrawlers
    club: CommandsUtilityBrawlstarsClub
    events: CommandsUtilityBrawlstarsEvents
    gameModes: CommandsUtilityBrawlstarsGameModes
    link: CommandsUtilityBrawlstarsLink
    maps: CommandsUtilityBrawlstarsMaps
    playerinfo: CommandsUtilityBrawlstarsPlayerinfo
    results: CommandsUtilityBrawlstarsResults
    unlink: CommandsUtilityBrawlstarsUnlink

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterchannel:
    already_claimed: CommandsUtilityClaimboosterchannelAlready_claimed
    category_not_found: CommandsUtilityClaimboosterchannelCategory_not_found
    expired: CommandsUtilityClaimboosterchannelExpired
    no_booster_channel: CommandsUtilityClaimboosterchannelNo_booster_channel
    no_booster_role: CommandsUtilityClaimboosterchannelNo_booster_role
    nobooster: CommandsUtilityClaimboosterchannelNobooster
    success: CommandsUtilityClaimboosterchannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterrole:
    already_claimed: CommandsUtilityClaimboosterroleAlready_claimed
    expired: CommandsUtilityClaimboosterroleExpired
    invalid_color: CommandsUtilityClaimboosterroleInvalid_color
    no_booster_role: CommandsUtilityClaimboosterroleNo_booster_role
    nobooster: CommandsUtilityClaimboosterroleNobooster
    role_not_found: CommandsUtilityClaimboosterroleRole_not_found
    success: CommandsUtilityClaimboosterroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityDeleteboosterchannel:
    missingPermission: CommandsUtilityDeleteboosterchannelMissingPermission
    no_booster_channel: CommandsUtilityDeleteboosterchannelNo_booster_channel
    success: CommandsUtilityDeleteboosterchannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityDeleteboosterrole:
    missingPermission: CommandsUtilityDeleteboosterroleMissingPermission
    no_booster_role: CommandsUtilityDeleteboosterroleNo_booster_role
    success: CommandsUtilityDeleteboosterroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityFeedback:
    blocked: CommandsUtilityFeedbackBlocked
    modal: CommandsUtilityFeedbackModal

@dataclass(frozen=True, slots=True)
class CommandsUtilityHelp:
    noDescriptionAvailable: LocalizedString
    parameters: LocalizedString
    title: LocalizedString
    titleNoPages: LocalizedString
    noCommands: CommandsUtilityHelpNoCommands

@dataclass(frozen=True, slots=True)
class CommandsUtilityListscheduled:
    cancel_button: LocalizedString
    direct_message: LocalizedString
    edit_button: LocalizedString
    message_details: LocalizedString
    message_id: LocalizedString
    no_repeat: LocalizedString
    title: LocalizedString
    edit_modal: CommandsUtilityListscheduledEdit_modal
    edit_success: CommandsUtilityListscheduledEdit_success
    error: CommandsUtilityListscheduledError
    no_messages: CommandsUtilityListscheduledNo_messages
    pagination: CommandsUtilityListscheduledPagination
    truncated: CommandsUtilityListscheduledTruncated

@dataclass(frozen=True, slots=True)
class CommandsUtilityMessagetrackingoptin:
    error: CommandsUtilityMessagetrackingoptinError
    success: CommandsUtilityMessagetrackingoptinSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityMessagetrackingoptout:
    error: CommandsUtilityMessagetrackingoptoutError
    success: CommandsUtilityMessagetrackingoptoutSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduled:
    error: CommandsUtilityRemovescheduledError
    no_messages: CommandsUtilityRemovescheduledNo_messages
    not_found: CommandsUtilityRemovescheduledNot_found
    select: CommandsUtilityRemovescheduledSelect
    success: CommandsUtilityRemovescheduledSuccess
    timeout: CommandsUtilityRemovescheduledTimeout

@dataclass(frozen=True, slots=True)
class CommandsUtilityReport:
    accept: CommandsUtilityReportAccept
    block_reporter: CommandsUtilityReportBlock_reporter
    blocked: CommandsUtilityReportBlocked
    invalid_action: CommandsUtilityReportInvalid_action
    new_report: CommandsUtilityReportNew_report
    no_permission: CommandsUtilityReportNo_permission
    no_reason: CommandsUtilityReportNo_reason
    no_report_channel: CommandsUtilityReportNo_report_channel
    reason_too_short: CommandsUtilityReportReason_too_short
    reject: CommandsUtilityReportReject
    report_channel_not_found: CommandsUtilityReportReport_channel_not_found
    report_sent: CommandsUtilityReportReport_sent
    reporter_blocked: CommandsUtilityReportReporter_blocked

@dataclass(frozen=True, slots=True)
class CommandsUtilityReports:
    accept: CommandsUtilityReportsAccept
    block_reporter: CommandsUtilityReportsBlock_reporter
    blocked: CommandsUtilityReportsBlocked
    invalid_action: CommandsUtilityReportsInvalid_action
    new_report: CommandsUtilityReportsNew_report
    no_permission: CommandsUtilityReportsNo_permission
    no_reason: CommandsUtilityReportsNo_reason
    no_report_channel: CommandsUtilityReportsNo_report_channel
    reason_too_short: CommandsUtilityReportsReason_too_short
    reject: CommandsUtilityReportsReject
    report_accepted: CommandsUtilityReportsReport_accepted
    report_channel_not_found: CommandsUtilityReportsReport_channel_not_found
    report_rejected: CommandsUtilityReportsReport_rejected
    report_sent: CommandsUtilityReportsReport_sent
    reporter_blocked: CommandsUtilityReportsReporter_blocked

@dataclass(frozen=True, slots=True)
class CommandsUtilitySchedulemessage:
    referenceMessage: LocalizedString
    invalidTime: CommandsUtilitySchedulemessageInvalidTime
    noBotChannelPermission: CommandsUtilitySchedulemessageNoBotChannelPermission
    noChannelPermission: CommandsUtilitySchedulemessageNoChannelPermission
    noDMPermission: CommandsUtilitySchedulemessageNoDMPermission
    noRepeatPermission: CommandsUtilitySchedulemessageNoRepeatPermission
    pastTime: CommandsUtilitySchedulemessagePastTime
    success: CommandsUtilitySchedulemessageSuccess
    tooManyScheduled: CommandsUtilitySchedulemessageTooManyScheduled

@dataclass(frozen=True, slots=True)
class CommandsUtilitySetupboosterchannel:
    already_set: CommandsUtilitySetupboosterchannelAlready_set
    missingPermission: CommandsUtilitySetupboosterchannelMissingPermission
    success: CommandsUtilitySetupboosterchannelSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilitySetupboosterrole:
    already_set: CommandsUtilitySetupboosterroleAlready_set
    missingPermission: CommandsUtilitySetupboosterroleMissingPermission
    success: CommandsUtilitySetupboosterroleSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitch:
    defaultNotificationMessage: LocalizedString
    addTwitchLiveNotification: CommandsUtilityTwitchAddTwitchLiveNotification
    listTwitchLiveNotifications: CommandsUtilityTwitchListTwitchLiveNotifications

@dataclass(frozen=True, slots=True)
class CommandsUtilityAvatar:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBanner:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityNoBanner:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAdd_roleMultipleSuccess:
    action: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleAlreadyHasRole:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleCancel:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleConfirm:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleManagedRole:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleNoRole:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleNoUser:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleRoleSelect:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleRoleTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleRoleTooHighBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAddroleUserSelect:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAdministrationTest_bot:
    all_completed: LocalizedString
    current_test_cmds: LocalizedString
    current_test_db: LocalizedString
    current_test_ping: LocalizedString
    error: LocalizedString
    starting: LocalizedString
    tests_unavailable: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAdministrationBenchmark_bot:
    error: LocalizedString
    starting: LocalizedString
    unavailable: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminAdministrationUpdate:
    connection_failed: LocalizedString
    http_error: LocalizedString
    updating: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBanError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBanForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBanMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBanMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBanSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBanTargetTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBoosterRoleError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBoosterRoleForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBoosterRoleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBoosterRoleMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBoosterRoleRoleRemoved:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBoosterRoleRoleTooHighBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBoosterRoleSuccess:
    description: LocalizedString
    descriptionWarning: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminBoosterRoleTargetTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelFarewell:
    defaultFarewellMessage: LocalizedString
    memberNumber: LocalizedString
    alreadySet: CommandsAdminChannelFarewellAlreadySet
    deleteSuccess: CommandsAdminChannelFarewellDeleteSuccess
    missingBotPermission: CommandsAdminChannelFarewellMissingBotPermission
    missingPermission: CommandsAdminChannelFarewellMissingPermission
    missingPro: CommandsAdminChannelFarewellMissingPro
    notSet: CommandsAdminChannelFarewellNotSet
    success: CommandsAdminChannelFarewellSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMedia:
    alreadySet: CommandsAdminChannelMediaAlreadySet
    deleteSuccess: CommandsAdminChannelMediaDeleteSuccess
    infoMessage: CommandsAdminChannelMediaInfoMessage
    infoMessageDelete: CommandsAdminChannelMediaInfoMessageDelete
    missingPermission: CommandsAdminChannelMediaMissingPermission
    missingPermissionBot: CommandsAdminChannelMediaMissingPermissionBot
    notSet: CommandsAdminChannelMediaNotSet
    onlyMedia: CommandsAdminChannelMediaOnlyMedia
    optedOut: CommandsAdminChannelMediaOptedOut
    success: CommandsAdminChannelMediaSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelWelcome:
    defaultWelcomeMessage: LocalizedString
    memberNumber: LocalizedString
    alreadySet: CommandsAdminChannelWelcomeAlreadySet
    deleteSuccess: CommandsAdminChannelWelcomeDeleteSuccess
    missingBotPermission: CommandsAdminChannelWelcomeMissingBotPermission
    missingPermission: CommandsAdminChannelWelcomeMissingPermission
    missingPro: CommandsAdminChannelWelcomeMissingPro
    notSet: CommandsAdminChannelWelcomeNotSet
    success: CommandsAdminChannelWelcomeSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminClose_ticketError:
    ticketNotFound1: LocalizedString
    ticketNotFound2: LocalizedString
    ticketNotFound3: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminClose_ticketButton:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminClose_ticketSuccess:
    description: LocalizedString
    ticketClosed: LocalizedString
    ticketClosedDescription: LocalizedString
    title: LocalizedString
    viewOnlineSummary: LocalizedString
    viewThread: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopy7tvAddModal:
    downloadError: LocalizedString
    error: LocalizedString
    invalidNumber: LocalizedString
    label: LocalizedString
    limitAnimated: LocalizedString
    limitStatic: LocalizedString
    placeholder: LocalizedString
    reason: LocalizedString
    title: LocalizedString
    success: CommandsAdminCopy7tvAddModalSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminCopy7tvError:
    notFound: CommandsAdminCopy7tvErrorNotFound

@dataclass(frozen=True, slots=True)
class CommandsAdminCopy7tvMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopy7tvMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmojiError:
    description: LocalizedString
    title: LocalizedString
    limitReached: CommandsAdminCopyEmojiErrorLimitReached
    noEmojis: CommandsAdminCopyEmojiErrorNoEmojis
    proRequired: CommandsAdminCopyEmojiErrorProRequired

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmojiSuccess:
    description: LocalizedString
    title: LocalizedString
    multiple: CommandsAdminCopyEmojiSuccessMultiple

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmojiMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmojiMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmojiPartialSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyroleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyroleMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateEmojiMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateEmojiSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreate_ticketButton:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreate_ticketEmbed:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreate_ticketError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreate_ticketMissingBotPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreate_ticketMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreate_ticketSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleHttp_error:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleIconTooLarge:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleInvalidColor:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleInvalidIcon:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleMissingName:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleNameTooLong:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleNotfound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleReasonTooLong:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleRoleIconsNotEnabled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCreateroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminDeleteroleForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminDeleteroleHttp_error:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminDeleteroleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminDeleteroleMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminDeleteroleNotfound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminDeleteroleRoleTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminDeleteroleRoleTooHighBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminDeleteroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedButtons:
    addField: LocalizedString
    editField: LocalizedString
    preview: LocalizedString
    removeField: LocalizedString
    send: LocalizedString
    setColor: LocalizedString
    setDescription: LocalizedString
    setFooter: LocalizedString
    setImage: LocalizedString
    setThumbnail: LocalizedString
    setTitle: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedModals:
    colorModal: CommandsAdminEmbedModalsColorModal
    editFieldModal: CommandsAdminEmbedModalsEditFieldModal
    fieldModal: CommandsAdminEmbedModalsFieldModal
    footerModal: CommandsAdminEmbedModalsFooterModal
    imageModal: CommandsAdminEmbedModalsImageModal
    removeFieldModal: CommandsAdminEmbedModalsRemoveFieldModal
    thumbnailModal: CommandsAdminEmbedModalsThumbnailModal
    titleModal: CommandsAdminEmbedModalsTitleModal

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedSetDescription:
    descriptionUpdated: LocalizedString
    message: LocalizedString
    timeout: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedMissingTitle:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminJoinToCreateListenerChannelDeleted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminJoinToCreateListenerSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminJointocreatechannelAlreadySet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminJointocreatechannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminJointocreatechannelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminKickError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminKickForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminKickMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminKickMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminKickSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminKickTargetTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminLockAlreadyLocked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminLockError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminLockForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminLockMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminLockMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminLockSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminMoveroleError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminMoveroleForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminMoveroleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminMoveroleMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminMoveroleRoleTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminMoveroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNicknameChanged:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNicknameError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNicknameForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNicknameMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNicknameMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNicknameRemoved:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNicknameTargetTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNukeMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNukeMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminNukeNotfound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminOpen_ticketError:
    channelMissingPermission: LocalizedString
    ticketCreated: LocalizedString
    ticketNotCreated: LocalizedString
    ticketNotFound: LocalizedString
    success: CommandsAdminOpen_ticketErrorSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminOpen_ticketSuccess:
    ticketCreated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminOpen_ticketOptedOutWarning:
    confirm: LocalizedString
    decline: LocalizedString
    declined: LocalizedString
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminPurgeError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminPurgeForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminPurgeInvalidAmount:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminPurgeMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminPurgeMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminPurgeSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_roleMultipleSuccess:
    action: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_timeoutError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_timeoutForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_timeoutMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_timeoutMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_timeoutNotTimedOut:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_timeoutSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemove_timeoutTargetTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemovejointocreatechannelAlreadySet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemovejointocreatechannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemovejointocreatechannelNotSet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemovejointocreatechannelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleCancel:
    _text: LocalizedString
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleConfirm:
    _text: LocalizedString
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleDoesNotHaveRole:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleManagedRole:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleNoRole:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleNoUser:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleRoleTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleRoleTooHighBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminRemoveroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsRemove_channel:
    missingPermission: CommandsAdminReportsRemove_channelMissingPermission
    noChannel: CommandsAdminReportsRemove_channelNoChannel
    success: CommandsAdminReportsRemove_channelSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsSet_channel:
    alreadySet: CommandsAdminReportsSet_channelAlreadySet
    missingPermission: CommandsAdminReportsSet_channelMissingPermission
    missingPermissionBot: CommandsAdminReportsSet_channelMissingPermissionBot
    success: CommandsAdminReportsSet_channelSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reports:
    not_your_reports: LocalizedString
    not_your_warns: LocalizedString
    block: CommandsAdminReportsShow_reportsBlock
    missingPermission: CommandsAdminReportsShow_reportsMissingPermission
    next: CommandsAdminReportsShow_reportsNext
    noReports: CommandsAdminReportsShow_reportsNoReports
    previous: CommandsAdminReportsShow_reportsPrevious
    remove: CommandsAdminReportsShow_reportsRemove
    report: CommandsAdminReportsShow_reportsReport
    resolve: CommandsAdminReportsShow_reportsResolve
    unblock: CommandsAdminReportsShow_reportsUnblock

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsUnblock_reporter:
    missingPermission: CommandsAdminReportsUnblock_reporterMissingPermission
    notBlocked: CommandsAdminReportsUnblock_reporterNotBlocked
    success: CommandsAdminReportsUnblock_reporterSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminSayError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSayMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSayMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSaySuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSetLocaleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSetLocaleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSlowmodeDisabled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSlowmodeEnabled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSlowmodeError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSlowmodeForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSlowmodeInvalidDuration:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSlowmodeMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminSlowmodeMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTimeoutAlreadyTimedOut:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTimeoutError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTimeoutForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTimeoutInvalidDuration:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTimeoutMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTimeoutMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTimeoutSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTimeoutTargetTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesAdd:
    missingPermission: CommandsAdminTrigger_messagesAddMissingPermission
    success: CommandsAdminTrigger_messagesAddSuccess

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigure:
    add_channel: CommandsAdminTrigger_messagesConfigureAdd_channel
    down: CommandsAdminTrigger_messagesConfigureDown
    missingPermission: CommandsAdminTrigger_messagesConfigureMissingPermission
    modal: CommandsAdminTrigger_messagesConfigureModal
    new: CommandsAdminTrigger_messagesConfigureNew
    next: CommandsAdminTrigger_messagesConfigureNext
    noTriggerMessages: CommandsAdminTrigger_messagesConfigureNoTriggerMessages
    previous: CommandsAdminTrigger_messagesConfigurePrevious
    remove: CommandsAdminTrigger_messagesConfigureRemove
    remove_channel: CommandsAdminTrigger_messagesConfigureRemove_channel
    trigger: CommandsAdminTrigger_messagesConfigureTrigger
    up: CommandsAdminTrigger_messagesConfigureUp

@dataclass(frozen=True, slots=True)
class CommandsAdminUnbanError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnbanForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnbanMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnbanMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnbanSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnbanUserNotFound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnlockError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnlockForbidden:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnlockMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnlockMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnlockNotLocked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminUnlockSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminViewwarnsMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminViewwarnsNoWarnings:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnReason:
    reached_warnings: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnDmNotification:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnTargetTooHigh:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigModal:
    title: LocalizedString
    ban_threshold: CommandsAdminWarnconfigModalBan_threshold
    kick_threshold: CommandsAdminWarnconfigModalKick_threshold
    timeout_duration: CommandsAdminWarnconfigModalTimeout_duration
    timeout_threshold: CommandsAdminWarnconfigModalTimeout_threshold
    warnexpiration: CommandsAdminWarnconfigModalWarnexpiration

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigCurrentConfig:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigError:
    invalidInput: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomAlreadyexists:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomInvalidfrequency_penalty:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomInvalidpresence_penalty:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomInvalidtemperature:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomInvalidtop_p:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomLongname:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomLongsituation:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomNamealreadyexists:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomNotplus:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomShortname:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomShortsituation:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAddcustomSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiApprovecustomSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAskError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAskNoapi:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAskNotoken:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiAskSuccess:
    footer: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiTokensSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiDeletecustomNotfound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiDeletecustomSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAiDencustomSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsChannelDynamicslowmodeAlreadySet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsChannelDynamicslowmodeChannels:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsChannelDynamicslowmodeDeleteSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsChannelDynamicslowmodeMissingBotPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsChannelDynamicslowmodeMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsChannelDynamicslowmodeNoChannels:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsChannelDynamicslowmodeNotSet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsChannelDynamicslowmodeSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesBattleshipError:
    invalidColumn: LocalizedString
    invalidCoordinate: LocalizedString
    invalidRow: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesConnect4Error:
    no_plus: CommandsGamesConnect4ErrorNo_plus

@dataclass(frozen=True, slots=True)
class CommandsGamesFlagquizButtons:
    giveUp: LocalizedString
    guess: LocalizedString
    hint: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesFlagquizError:
    hintUsed: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesFlagquizModal:
    title: LocalizedString
    input: CommandsGamesFlagquizModalInput

@dataclass(frozen=True, slots=True)
class CommandsGamesFlagquizFailure:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesFlagquizGivenUp:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesFlagquizInitial:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesFlagquizSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesHangmanButtons:
    giveUp: LocalizedString
    guess: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesHangmanModal:
    title: LocalizedString
    input: CommandsGamesHangmanModalInput

@dataclass(frozen=True, slots=True)
class CommandsGamesHangmanError:
    description: LocalizedString
    invalidInput: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesHangmanFailure:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesHangmanGivenUp:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesHangmanInitial:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesHangmanSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesHangmanWrongGuess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleButtons:
    giveUp: LocalizedString
    guess: LocalizedString
    playHard: LocalizedString
    playNormal: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleInitial:
    description: LocalizedString
    title: LocalizedString
    descriptionextra: CommandsGamesWordleInitialDescriptionextra

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleModal:
    title: LocalizedString
    input: CommandsGamesWordleModalInput

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleError:
    description: LocalizedString
    invalidInput: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleFailure:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleGivenUp:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleHardMode:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordlePickMode:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleStats:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayAdd_blacklist_roleAlreadyBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayAdd_blacklist_roleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayAdd_blacklist_rolePro_required:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayAdd_blacklist_roleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayAdd_blacklist_userAlreadyBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayAdd_blacklist_userMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayAdd_blacklist_userSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderAdd_channel_requirement:
    cancelled: LocalizedString
    label: LocalizedString
    placeholder: LocalizedString
    removed: LocalizedString
    select: LocalizedString
    v: CommandsGiveawayBuilderAdd_channel_requirementV
    value: CommandsGiveawayBuilderAdd_channel_requirementValue

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderChannel:
    selected: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderDescription:
    timeout: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderModal:
    timeout: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderSponsor:
    cancelled: LocalizedString
    label: LocalizedString
    selected: LocalizedString
    updated: LocalizedString
    select: CommandsGiveawayBuilderSponsorSelect

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderWinner:
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderChange_winners:
    description: LocalizedString
    label: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderCustom_name:
    description: LocalizedString
    label: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderDay_requirement:
    description: LocalizedString
    label: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderEnd_time:
    description: LocalizedString
    label: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderMessage:
    label: LocalizedString
    timeout: LocalizedString
    too_long: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderNew_message_requirement:
    description: LocalizedString
    label: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderPrice:
    label: LocalizedString
    timeout: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderRemove_channel_requirement:
    label: LocalizedString
    placeholder: LocalizedString
    removed: LocalizedString
    select: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderRole_requirement:
    cancelled: LocalizedString
    description: LocalizedString
    label: LocalizedString
    placeholder: LocalizedString
    pro: LocalizedString
    select: LocalizedString
    title: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderStart_time:
    description: LocalizedString
    label: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderVoice_requirement:
    description: LocalizedString
    label: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEditorSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveawayError:
    already_ended: CommandsGiveawayEnd_giveawayErrorAlready_ended
    invalid_message: CommandsGiveawayEnd_giveawayErrorInvalid_message
    missingPermission: CommandsGiveawayEnd_giveawayErrorMissingPermission
    no_permission: CommandsGiveawayEnd_giveawayErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveawayDeleted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveawaySuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveaway_commandError:
    alreadyEnded: CommandsGiveawayEnd_giveaway_commandErrorAlreadyEnded
    missingPermission: CommandsGiveawayEnd_giveaway_commandErrorMissingPermission
    notFound: CommandsGiveawayEnd_giveaway_commandErrorNotFound

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveaway_commandDeleted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveaway_commandSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEndedGiveawayNo_participants:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayGiveawayEmbedParticipation_failed:
    blacklisted: LocalizedString
    blacklisted_role: LocalizedString
    channel_requirements: LocalizedString
    day_requirement: LocalizedString
    message_requirement: LocalizedString
    opted_out: LocalizedString
    role_requirement: LocalizedString
    title: LocalizedString
    voice_requirement: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayGiveawayEmbedParticipation_removed:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayGiveawayEmbedParticipation_success:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayList_blacklistMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayList_blacklistNoBlacklist:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayRemove_blacklist_roleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayRemove_blacklist_roleNotBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayRemove_blacklist_roleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayRemove_blacklist_userMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayRemove_blacklist_userNotBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayRemove_blacklist_userSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayReroll_giveawayError:
    notAuthorized: LocalizedString
    missingPermission: CommandsGiveawayReroll_giveawayErrorMissingPermission
    noParticipants: CommandsGiveawayReroll_giveawayErrorNoParticipants
    notEnded: CommandsGiveawayReroll_giveawayErrorNotEnded
    notFound: CommandsGiveawayReroll_giveawayErrorNotFound

@dataclass(frozen=True, slots=True)
class CommandsGiveawayReroll_giveawaySelectOption:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayReroll_giveawaySuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageBackgroundDisabled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageBackgroundSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageBlurSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageCompressSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageContourSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageDetailSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageEdgeenhanceSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageEmbossSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageErrorUnknown_filter:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageFindedgesSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageMirrorInvalidaxis:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageMirrorSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageRescaleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageResizeSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageSharpenSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsImageSmoothSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelAddlevelroleError:
    invalid_level: CommandsLevelAddlevelroleErrorInvalid_level
    no_permission: CommandsLevelAddlevelroleErrorNo_permission
    no_pro: CommandsLevelAddlevelroleErrorNo_pro
    role_exists: CommandsLevelAddlevelroleErrorRole_exists

@dataclass(frozen=True, slots=True)
class CommandsLevelAddlevelroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_channel:
    error: CommandsLevelBlacklistAdd_channelError
    success: CommandsLevelBlacklistAdd_channelSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_role:
    error: CommandsLevelBlacklistAdd_roleError
    success: CommandsLevelBlacklistAdd_roleSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_user:
    error: CommandsLevelBlacklistAdd_userError
    success: CommandsLevelBlacklistAdd_userSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_channel:
    error: CommandsLevelBlacklistRemove_channelError
    success: CommandsLevelBlacklistRemove_channelSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_role:
    error: CommandsLevelBlacklistRemove_roleError
    success: CommandsLevelBlacklistRemove_roleSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_user:
    error: CommandsLevelBlacklistRemove_userError
    success: CommandsLevelBlacklistRemove_userSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistShow:
    channels: LocalizedString
    description: LocalizedString
    empty: LocalizedString
    roles: LocalizedString
    title: LocalizedString
    users: LocalizedString
    error: CommandsLevelBlacklistShowError

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsAdd_channel:
    success: CommandsLevelBoostsAdd_channelSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsAdd_role:
    success: CommandsLevelBoostsAdd_roleSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsAdd_user:
    success: CommandsLevelBoostsAdd_userSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsError:
    no_pro: CommandsLevelBoostsErrorNo_pro

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsRemove_channel:
    success: CommandsLevelBoostsRemove_channelSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsRemove_role:
    success: CommandsLevelBoostsRemove_roleSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsRemove_user:
    success: CommandsLevelBoostsRemove_userSuccess

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsCalculate_user_channel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsShow:
    channels: LocalizedString
    description: LocalizedString
    no_boosts: LocalizedString
    roles: LocalizedString
    title: LocalizedString
    users: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangelevelupmessageError:
    message_too_long: CommandsLevelChangelevelupmessageErrorMessage_too_long
    no_permission: CommandsLevelChangelevelupmessageErrorNo_permission
    no_pro: CommandsLevelChangelevelupmessageErrorNo_pro

@dataclass(frozen=True, slots=True)
class CommandsLevelChangelevelupmessageSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangexpscalingError:
    invalid_scaling: CommandsLevelChangexpscalingErrorInvalid_scaling
    no_custom_formula: CommandsLevelChangexpscalingErrorNo_custom_formula
    no_permission: CommandsLevelChangexpscalingErrorNo_permission
    no_pro: CommandsLevelChangexpscalingErrorNo_pro

@dataclass(frozen=True, slots=True)
class CommandsLevelChangexpscalingFormulas:
    easy: LocalizedString
    extreme: LocalizedString
    hard: LocalizedString
    medium: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangexpscalingScalings:
    custom: LocalizedString
    easy: LocalizedString
    extreme: LocalizedString
    hard: LocalizedString
    medium: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangexpscalingSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelsystemError:
    already_disabled: CommandsLevelDisablelevelsystemErrorAlready_disabled
    no_permission: CommandsLevelDisablelevelsystemErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelsystemCancel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelsystemConfirmation:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelsystemSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelupmessageError:
    already_disabled: CommandsLevelDisablelevelupmessageErrorAlready_disabled
    no_permission: CommandsLevelDisablelevelupmessageErrorNo_permission
    no_pro: CommandsLevelDisablelevelupmessageErrorNo_pro

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelupmessageSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelsystemError:
    already_enabled: CommandsLevelEnablelevelsystemErrorAlready_enabled
    no_permission: CommandsLevelEnablelevelsystemErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelsystemSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelupmessageError:
    already_enabled: CommandsLevelEnablelevelupmessageErrorAlready_enabled
    no_permission: CommandsLevelEnablelevelupmessageErrorNo_permission
    no_pro: CommandsLevelEnablelevelupmessageErrorNo_pro

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelupmessageSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelGivexpError:
    invalid_amount: CommandsLevelGivexpErrorInvalid_amount
    no_permission: CommandsLevelGivexpErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelGivexpSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelRankData:
    level: LocalizedString
    xp: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelRankError:
    no_data: CommandsLevelRankErrorNo_data

@dataclass(frozen=True, slots=True)
class CommandsLevelRankSuccess:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelRemovelevelroleError:
    no_permission: CommandsLevelRemovelevelroleErrorNo_permission
    no_pro: CommandsLevelRemovelevelroleErrorNo_pro
    role_not_found: CommandsLevelRemovelevelroleErrorRole_not_found

@dataclass(frozen=True, slots=True)
class CommandsLevelRemovelevelroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetbackgroundError:
    invalid_format: CommandsLevelSetbackgroundErrorInvalid_format
    no_plus: CommandsLevelSetbackgroundErrorNo_plus

@dataclass(frozen=True, slots=True)
class CommandsLevelSetbackgroundSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetlevelupchannelError:
    no_permission: CommandsLevelSetlevelupchannelErrorNo_permission
    no_pro: CommandsLevelSetlevelupchannelErrorNo_pro

@dataclass(frozen=True, slots=True)
class CommandsLevelSetlevelupchannelReset:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetlevelupchannelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSettextcooldownError:
    invalid_cooldown: CommandsLevelSettextcooldownErrorInvalid_cooldown
    no_permission: CommandsLevelSettextcooldownErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelSettextcooldownParams:
    cooldown: CommandsLevelSettextcooldownParamsCooldown

@dataclass(frozen=True, slots=True)
class CommandsLevelSettextcooldownSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetvoicecooldownError:
    invalid_cooldown: CommandsLevelSetvoicecooldownErrorInvalid_cooldown
    no_permission: CommandsLevelSetvoicecooldownErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelSetvoicecooldownParams:
    cooldown: CommandsLevelSetvoicecooldownParamsCooldown

@dataclass(frozen=True, slots=True)
class CommandsLevelSetvoicecooldownSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetxpError:
    invalid_amount: CommandsLevelSetxpErrorInvalid_amount
    no_permission: CommandsLevelSetxpErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelSetxpSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelShowlevelrolesError:
    no_permission: CommandsLevelShowlevelrolesErrorNo_permission
    no_pro: CommandsLevelShowlevelrolesErrorNo_pro

@dataclass(frozen=True, slots=True)
class CommandsLevelShowlevelrolesRemove_role_confirm:
    cancel_button: LocalizedString
    confirm_button: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelShowlevelrolesAdd_role_modal:
    invalid_level: LocalizedString
    level_label: LocalizedString
    level_placeholder: LocalizedString
    success: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelShowlevelrolesNo_roles:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelShowlevelrolesSelected_level:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelTakexpError:
    invalid_amount: CommandsLevelTakexpErrorInvalid_amount
    no_permission: CommandsLevelTakexpErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelTakexpSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistAdd:
    description: LocalizedString
    name: LocalizedString
    params: CommandsLogsBlacklistAddParams

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemove:
    description: LocalizedString
    name: LocalizedString
    params: CommandsLogsBlacklistRemoveParams

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistShow:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistCategoryAlreadyBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistCategoryBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistCategoryMissingChannel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistCategoryMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistChannelAlreadyBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistChannelBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistChannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListCategoryAddCategory:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListCategoryMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListChannelAddChannel:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListChannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListRoleAddRole:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListRoleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListUserAddUser:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListUserMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListVoiceChannelAddChannel:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistListVoiceChannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveCategoryMissingChannel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveCategoryMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveCategoryNotBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveCategorySuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveChannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveChannelNotBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveChannelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveRoleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveRoleNotBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveRoleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveUserMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveUserNotBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveUserSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveVoiceChannelMissingChannel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveVoiceChannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveVoiceChannelNotBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveVoiceChannelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRoleAlreadyBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRoleBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRoleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistUserAlreadyBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistUserBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistUserMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistVoiceChannelAlreadyBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistVoiceChannelBlacklisted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistVoiceChannelMissingChannel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistVoiceChannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsConfigureLogsConfiguration_embed:
    activate: LocalizedString
    activated: LocalizedString
    automodAction: LocalizedString
    automodRuleCreate: LocalizedString
    automodRuleDelete: LocalizedString
    automodRuleUpdate: LocalizedString
    deactivate: LocalizedString
    deactivated: LocalizedString
    guildRoleCreate: LocalizedString
    guildRoleDelete: LocalizedString
    guildRoleUpdate: LocalizedString
    guildUpdate: LocalizedString
    guild_channelCreate: LocalizedString
    guild_channelDelete: LocalizedString
    guild_channelUpdate: LocalizedString
    inviteCreate: LocalizedString
    inviteDelete: LocalizedString
    memberBan: LocalizedString
    memberJoin: LocalizedString
    memberLeave: LocalizedString
    memberUnban: LocalizedString
    memberUpdate: LocalizedString
    messageDelete: LocalizedString
    messageEdit: LocalizedString
    presenceUpdate: LocalizedString
    reactionAdd: LocalizedString
    reactionRemove: LocalizedString
    userUpdate: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsConfigureLogsConfigurationEmbed:
    activate: LocalizedString
    activated: LocalizedString
    automodAction: LocalizedString
    automodRuleCreate: LocalizedString
    automodRuleDelete: LocalizedString
    automodRuleUpdate: LocalizedString
    deactivate: LocalizedString
    deactivated: LocalizedString
    guildChannelCreate: LocalizedString
    guildChannelDelete: LocalizedString
    guildChannelUpdate: LocalizedString
    guildRoleCreate: LocalizedString
    guildRoleDelete: LocalizedString
    guildRoleUpdate: LocalizedString
    guildUpdate: LocalizedString
    inviteCreate: LocalizedString
    inviteDelete: LocalizedString
    memberBan: LocalizedString
    memberJoin: LocalizedString
    memberLeave: LocalizedString
    memberUnban: LocalizedString
    memberUpdate: LocalizedString
    messageDelete: LocalizedString
    messageEdit: LocalizedString
    presenceUpdate: LocalizedString
    reactionAdd: LocalizedString
    reactionRemove: LocalizedString
    title: LocalizedString
    userUpdate: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsConfigureLogsNoLogEnabled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsRemoveLogChannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsRemoveLogChannelNotSet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsRemoveLogChannelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsSetLogChannelAlreadySet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsSetLogChannelBotMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsSetLogChannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsSetLogChannelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathCalcError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathCalcSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathFacultyError:
    invalid_input: LocalizedString
    invalid_number: LocalizedString
    invalid_number2: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathFacultySuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathNum2wordLocales:
    am: LocalizedString
    ar: LocalizedString
    az: LocalizedString
    by: LocalizedString
    ce: LocalizedString
    cy: LocalizedString
    cz: LocalizedString
    de: LocalizedString
    dk: LocalizedString
    eu: LocalizedString
    fa: LocalizedString
    fi: LocalizedString
    he: LocalizedString
    hu: LocalizedString
    id: LocalizedString
    is_: LocalizedString
    it: LocalizedString
    ja: LocalizedString
    kn: LocalizedString
    ko: LocalizedString
    kz: LocalizedString
    lt: LocalizedString
    lv: LocalizedString
    nl: LocalizedString
    no: LocalizedString
    pl: LocalizedString
    ro: LocalizedString
    ru: LocalizedString
    sl: LocalizedString
    sr: LocalizedString
    sv: LocalizedString
    te: LocalizedString
    tg: LocalizedString
    th: LocalizedString
    tr: LocalizedString
    uk: LocalizedString
    vi: LocalizedString
    en: CommandsMathNum2wordLocalesEn
    es: CommandsMathNum2wordLocalesEs
    fr: CommandsMathNum2wordLocalesFr
    pt: CommandsMathNum2wordLocalesPt

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionButtons:
    add_function: LocalizedString
    change_style: LocalizedString
    change_x_label: LocalizedString
    change_y_label: LocalizedString
    derive: LocalizedString
    integrate: LocalizedString
    move_down: LocalizedString
    move_left: LocalizedString
    move_right: LocalizedString
    move_up: LocalizedString
    rename_function: LocalizedString
    rename_plot: LocalizedString
    zoom_in: LocalizedString
    zoom_out: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionMessages:
    error_occurred: LocalizedString
    function_added: LocalizedString
    function_derived: LocalizedString
    function_integrated: LocalizedString
    function_renamed: LocalizedString
    no_permission: LocalizedString
    plot_updated: LocalizedString
    style_changed: LocalizedString
    title_changed: LocalizedString
    x_label_changed: LocalizedString
    y_label_changed: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionModals:
    add_function: CommandsMathPlotfunctionModalsAdd_function
    change_title: CommandsMathPlotfunctionModalsChange_title
    change_x_label: CommandsMathPlotfunctionModalsChange_x_label
    change_y_label: CommandsMathPlotfunctionModalsChange_y_label
    rename_function: CommandsMathPlotfunctionModalsRename_function

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionSelect_menus:
    derive: CommandsMathPlotfunctionSelect_menusDerive
    integrate: CommandsMathPlotfunctionSelect_menusIntegrate
    rename_function: CommandsMathPlotfunctionSelect_menusRename_function
    style: CommandsMathPlotfunctionSelect_menusStyle

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionError:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathRandomnumberError:
    invalid_amount: LocalizedString
    invalid_input: LocalizedString
    invalid_range: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathRandomnumberSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAfkAlready_afk:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAfkMentions:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAfkMentions_one:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAfkOpted_out:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAfkRemoved:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAfkRemoved_no_messages:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAfkSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAutopublishError:
    is_already: CommandsUtilityAutopublishErrorIs_already
    is_not: CommandsUtilityAutopublishErrorIs_not
    no_permission: CommandsUtilityAutopublishErrorNo_permission
    not_news_channel: CommandsUtilityAutopublishErrorNot_news_channel

@dataclass(frozen=True, slots=True)
class CommandsUtilityAutopublishRemove_success:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAutopublishSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAvatarDecorationNo_decoration:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBoosterchannelinfoInfo:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBoosterroleinfoInfo:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBattlelog:
    title: LocalizedString
    titleNoPages: LocalizedString
    description: CommandsUtilityBrawlstarsBattlelogDescription
    error: CommandsUtilityBrawlstarsBattlelogError

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBrawlers:
    title: LocalizedString
    titleNoPages: LocalizedString
    description: CommandsUtilityBrawlstarsBrawlersDescription
    error: CommandsUtilityBrawlstarsBrawlersError
    search: CommandsUtilityBrawlstarsBrawlersSearch

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsClub:
    title: LocalizedString
    titleNoMembers: LocalizedString
    description: CommandsUtilityBrawlstarsClubDescription
    error: CommandsUtilityBrawlstarsClubError
    search: CommandsUtilityBrawlstarsClubSearch

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsEvents:
    description: LocalizedString
    notYourEmbed: LocalizedString
    title: LocalizedString
    titleNoPages: LocalizedString
    error: CommandsUtilityBrawlstarsEventsError
    notFound: CommandsUtilityBrawlstarsEventsNotFound

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsGameModes:
    bounty: LocalizedString
    brawlBall: LocalizedString
    brawlBall5V5: LocalizedString
    duels: LocalizedString
    duoShowdown: LocalizedString
    gemGrab: LocalizedString
    heist: LocalizedString
    hotZone: LocalizedString
    knockout: LocalizedString
    soloShowdown: LocalizedString
    unknown: LocalizedString
    wipeout: LocalizedString
    wipeout5V5: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsLink:
    error: CommandsUtilityBrawlstarsLinkError
    success: CommandsUtilityBrawlstarsLinkSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsMaps:
    Gg_2_0: LocalizedString
    H_For___: LocalizedString
    Acid_Cavern_Churn: LocalizedString
    Acid_Lakes: LocalizedString
    Backyard_Bowl: LocalizedString
    Beach_Ball: LocalizedString
    Belles_Rock: LocalizedString
    Broiler_Room: LocalizedString
    Canal_Grande: LocalizedString
    Cavern_Churn: LocalizedString
    Center_Stage: LocalizedString
    Cool_shapes: LocalizedString
    Crystal_Arcade: LocalizedString
    Dark_Passage: LocalizedString
    Deathcap_Trap: LocalizedString
    Deep_Forest: LocalizedString
    Double_Swoosh: LocalizedString
    Double_Trouble: LocalizedString
    Dried_Up_River: LocalizedString
    Dueling_Beetles: LocalizedString
    Feast_Or_Famine: LocalizedString
    Final_Four: LocalizedString
    Flarning_Phoenix: LocalizedString
    Flying_Fantasies: LocalizedString
    Forest_Clearing: LocalizedString
    Four_Levels: LocalizedString
    Freezig_Ripples: LocalizedString
    Frosty_Tracks: LocalizedString
    Gem_Fort: LocalizedString
    Goldarm_Gulch: LocalizedString
    Great_Waves: LocalizedString
    Hard_Rock_Mine: LocalizedString
    Hideout: LocalizedString
    Hoop_Boot_Hill: LocalizedString
    Hot_Potato: LocalizedString
    Icy_ice_park: LocalizedString
    Infinite_Doom: LocalizedString
    Island_Invasion: LocalizedString
    Kaboom_Canyon: LocalizedString
    Last_Stop: LocalizedString
    Layer_Bake: LocalizedString
    Layer_Cake: LocalizedString
    Marksman_s_Paradise: LocalizedString
    Minecard_Madness: LocalizedString
    Monkey_Maze: LocalizedString
    New_Horizons: LocalizedString
    No_Excuses: LocalizedString
    No_Surrender: LocalizedString
    Noisy_Neighbors: LocalizedString
    Open_Business: LocalizedString
    Open_Space: LocalizedString
    Out_In_The_Open: LocalizedString
    Overgrown_Ruins: LocalizedString
    Parallel_Plays: LocalizedString
    Penalty_Kick: LocalizedString
    Petticoat_Duel: LocalizedString
    Pinball_Dreams: LocalizedString
    Pinhole_Punt: LocalizedString
    Quad_Damage: LocalizedString
    Ring_Of_File: LocalizedString
    Riverbank_Crossing: LocalizedString
    Rockwall_Brawl: LocalizedString
    Rustic_Arcade: LocalizedString
    Safe_Zone: LocalizedString
    Safe_r__Zone: LocalizedString
    Safety_Center: LocalizedString
    Second_Try: LocalizedString
    Shooting_Star: LocalizedString
    Shrouding_Serpent: LocalizedString
    Skull_Creek: LocalizedString
    Skull_Rockwall_Brawl: LocalizedString
    Slayers_Paradise: LocalizedString
    Slippery_Road: LocalizedString
    Snake_Prairie: LocalizedString
    Sneaky_Fields: LocalizedString
    Spie_Production: LocalizedString
    Sunny_Soccer: LocalizedString
    Super_Beach: LocalizedString
    Suspenders: LocalizedString
    Temple_Of_Vroom: LocalizedString
    The_Cooler_Hard_Rock: LocalizedString
    The_Great_Lake: LocalizedString
    The_Great_Open: LocalizedString
    Tiny_Islands: LocalizedString
    Trickey: LocalizedString
    Triple_Dribble: LocalizedString
    Two_Rivers: LocalizedString
    Undermine: LocalizedString
    Warrioirs_Way: LocalizedString
    Watersport: LocalizedString
    Zen_Garden: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsPlayerinfo:
    title: LocalizedString
    description: CommandsUtilityBrawlstarsPlayerinfoDescription
    error: CommandsUtilityBrawlstarsPlayerinfoError

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsResults:
    defeat: LocalizedString
    draw: LocalizedString
    victory: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsUnlink:
    error: CommandsUtilityBrawlstarsUnlinkError
    success: CommandsUtilityBrawlstarsUnlinkSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterchannelExpired:
    reason: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterchannelAlready_claimed:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterchannelCategory_not_found:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterchannelNo_booster_channel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterchannelNo_booster_role:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterchannelNobooster:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterchannelSuccess:
    description: LocalizedString
    reason: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterroleExpired:
    reason: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterroleAlready_claimed:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterroleInvalid_color:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterroleNo_booster_role:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterroleNobooster:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterroleRole_not_found:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityClaimboosterroleSuccess:
    description: LocalizedString
    reason: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityDeleteboosterchannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityDeleteboosterchannelNo_booster_channel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityDeleteboosterchannelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityDeleteboosterroleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityDeleteboosterroleNo_booster_role:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityDeleteboosterroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityFeedbackModal:
    description: LocalizedString
    not_authorized: LocalizedString
    timeout: LocalizedString
    title: LocalizedString
    feedbackdescription: CommandsUtilityFeedbackModalFeedbackdescription
    feedbacktitle: CommandsUtilityFeedbackModalFeedbacktitle
    submitted: CommandsUtilityFeedbackModalSubmitted
    timeout: CommandsUtilityFeedbackModalTimeout

@dataclass(frozen=True, slots=True)
class CommandsUtilityFeedbackBlocked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityHelpNoCommands:
    description: LocalizedString
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityListscheduledError:
    not_authorized: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityListscheduledPagination:
    page_counter: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityListscheduledEdit_modal:
    content_label: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityListscheduledEdit_success:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityListscheduledNo_messages:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityListscheduledTruncated:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityMessagetrackingoptinError:
    already_opted_in: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityMessagetrackingoptinSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityMessagetrackingoptoutError:
    already_opted_out: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityMessagetrackingoptoutSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduledError:
    not_authorized: LocalizedString
    no_messages: CommandsUtilityRemovescheduledErrorNo_messages
    not_found: CommandsUtilityRemovescheduledErrorNot_found
    timeout: CommandsUtilityRemovescheduledErrorTimeout

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduledNo_messages:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduledNot_found:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduledSelect:
    description: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduledSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduledTimeout:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportAccept:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportBlock_reporter:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportBlocked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportInvalid_action:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportNew_report:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportNo_reason:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportNo_report_channel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportReason_too_short:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportReject:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportReport_channel_not_found:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportReport_sent:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportReporter_blocked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsAccept:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsBlock_reporter:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsBlocked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsInvalid_action:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsNew_report:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsNo_reason:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsNo_report_channel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsReason_too_short:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsReject:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsReport_accepted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsReport_channel_not_found:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsReport_rejected:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsReport_sent:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityReportsReporter_blocked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySchedulemessageInvalidTime:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySchedulemessageNoBotChannelPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySchedulemessageNoChannelPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySchedulemessageNoDMPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySchedulemessageNoRepeatPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySchedulemessagePastTime:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySchedulemessageSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySchedulemessageTooManyScheduled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySetupboosterchannelAlready_set:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySetupboosterchannelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySetupboosterchannelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySetupboosterroleAlready_set:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySetupboosterroleMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilitySetupboosterroleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotification:
    error: CommandsUtilityTwitchAddTwitchLiveNotificationError
    errors: CommandsUtilityTwitchAddTwitchLiveNotificationErrors
    success: CommandsUtilityTwitchAddTwitchLiveNotificationSuccess

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchListTwitchLiveNotifications:
    description: LocalizedString
    title: LocalizedString
    titleNoPages: LocalizedString
    error: CommandsUtilityTwitchListTwitchLiveNotificationsError

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelFarewellAlreadySet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelFarewellDeleteSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelFarewellMissingBotPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelFarewellMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelFarewellMissingPro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelFarewellNotSet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelFarewellSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaAlreadySet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaDeleteSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaInfoMessage:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaInfoMessageDelete:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaNotSet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaOnlyMedia:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaOptedOut:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelMediaSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelWelcomeAlreadySet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelWelcomeDeleteSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelWelcomeMissingBotPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelWelcomeMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelWelcomeMissingPro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelWelcomeNotSet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminChannelWelcomeSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopy7tvAddModalSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopy7tvErrorNotFound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmojiErrorLimitReached:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmojiErrorNoEmojis:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmojiErrorProRequired:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminCopyEmojiSuccessMultiple:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedModalsColorModal:
    label: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedModalsEditFieldModal:
    fieldLabel: LocalizedString
    selectField: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedModalsFieldModal:
    inlineLabel: LocalizedString
    nameLabel: LocalizedString
    title: LocalizedString
    valueLabel: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedModalsFooterModal:
    iconLabel: LocalizedString
    label: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedModalsImageModal:
    label: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedModalsRemoveFieldModal:
    fieldLabel: LocalizedString
    selectField: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedModalsThumbnailModal:
    label: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminEmbedModalsTitleModal:
    label: LocalizedString
    title: LocalizedString
    urlLabel: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminOpen_ticketErrorSuccess:
    ticketCreated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsRemove_channelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsRemove_channelNoChannel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsRemove_channelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsSet_channelAlreadySet:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsSet_channelMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsSet_channelMissingPermissionBot:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsSet_channelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reportsBlock:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reportsMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reportsNext:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reportsNoReports:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reportsPrevious:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reportsRemove:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reportsReport:
    accepted: LocalizedString
    description: LocalizedString
    not_accepted: LocalizedString
    not_resolved: LocalizedString
    resolved: LocalizedString
    status: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reportsResolve:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsShow_reportsUnblock:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsUnblock_reporterMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsUnblock_reporterNotBlocked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminReportsUnblock_reporterSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesAddMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesAddSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureModal:
    title: LocalizedString
    caseSensitive: CommandsAdminTrigger_messagesConfigureModalCaseSensitive
    case_sensitive: CommandsAdminTrigger_messagesConfigureModalCase_sensitive
    response: CommandsAdminTrigger_messagesConfigureModalResponse
    trigger: CommandsAdminTrigger_messagesConfigureModalTrigger

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureTrigger:
    caseInsensitive: LocalizedString
    caseSensitive: LocalizedString
    case_sensitive: LocalizedString
    channels: LocalizedString
    description: LocalizedString
    noChannels: LocalizedString
    title: LocalizedString
    addChannel: CommandsAdminTrigger_messagesConfigureTriggerAddChannel
    noTriggerMessages: CommandsAdminTrigger_messagesConfigureTriggerNoTriggerMessages

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureAdd_channel:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureDown:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureNew:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureNext:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureNoTriggerMessages:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigurePrevious:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureRemove:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureRemove_channel:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureUp:
    label: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigModalBan_threshold:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigModalKick_threshold:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigModalTimeout_duration:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigModalTimeout_threshold:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminWarnconfigModalWarnexpiration:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesConnect4ErrorNo_plus:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesFlagquizModalInput:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesHangmanModalInput:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleInitialDescriptionextra:
    ja: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGamesWordleModalInput:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderAdd_channel_requirementV:
    p: LocalizedString
    t: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderAdd_channel_requirementValue:
    description: LocalizedString
    updated: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayBuilderSponsorSelect:
    name: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveawayErrorAlready_ended:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveawayErrorInvalid_message:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveawayErrorMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveawayErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveaway_commandErrorAlreadyEnded:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveaway_commandErrorMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayEnd_giveaway_commandErrorNotFound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayReroll_giveawayErrorMissingPermission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayReroll_giveawayErrorNoParticipants:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayReroll_giveawayErrorNotEnded:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsGiveawayReroll_giveawayErrorNotFound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelAddlevelroleErrorInvalid_level:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelAddlevelroleErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelAddlevelroleErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelAddlevelroleErrorRole_exists:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_channelError:
    no_permission: CommandsLevelBlacklistAdd_channelErrorNo_permission
    no_pro: CommandsLevelBlacklistAdd_channelErrorNo_pro

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_channelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_roleError:
    no_permission: CommandsLevelBlacklistAdd_roleErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_roleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_userError:
    no_permission: CommandsLevelBlacklistAdd_userErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_userSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_channelError:
    no_permission: CommandsLevelBlacklistRemove_channelErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_channelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_roleError:
    no_permission: CommandsLevelBlacklistRemove_roleErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_roleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_userError:
    no_permission: CommandsLevelBlacklistRemove_userErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_userSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistShowError:
    no_permission: CommandsLevelBlacklistShowErrorNo_permission

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsAdd_channelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsAdd_roleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsAdd_userSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsRemove_channelSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsRemove_roleSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBoostsRemove_userSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangelevelupmessageErrorMessage_too_long:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangelevelupmessageErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangelevelupmessageErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangexpscalingErrorInvalid_scaling:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangexpscalingErrorNo_custom_formula:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangexpscalingErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelChangexpscalingErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelsystemErrorAlready_disabled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelsystemErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelupmessageErrorAlready_disabled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelupmessageErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelDisablelevelupmessageErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelsystemErrorAlready_enabled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelsystemErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelupmessageErrorAlready_enabled:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelupmessageErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelEnablelevelupmessageErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelGivexpErrorInvalid_amount:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelGivexpErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelRankErrorNo_data:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelRemovelevelroleErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelRemovelevelroleErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelRemovelevelroleErrorRole_not_found:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetbackgroundErrorInvalid_format:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetbackgroundErrorNo_plus:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetlevelupchannelErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetlevelupchannelErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSettextcooldownErrorInvalid_cooldown:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSettextcooldownErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSettextcooldownParamsCooldown:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetvoicecooldownErrorInvalid_cooldown:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetvoicecooldownErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetvoicecooldownParamsCooldown:
    description: LocalizedString
    name: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetxpErrorInvalid_amount:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelSetxpErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelShowlevelrolesErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelShowlevelrolesErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelTakexpErrorInvalid_amount:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelTakexpErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistAddParams:
    channel: CommandsLogsBlacklistAddParamsChannel

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveParams:
    channel: CommandsLogsBlacklistRemoveParamsChannel

@dataclass(frozen=True, slots=True)
class CommandsMathNum2wordLocalesEn:
    GB: LocalizedString
    IN: LocalizedString
    NG: LocalizedString
    _text: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathNum2wordLocalesEs:
    CO: LocalizedString
    CR: LocalizedString
    GT: LocalizedString
    VE: LocalizedString
    _text: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathNum2wordLocalesFr:
    BE: LocalizedString
    CH: LocalizedString
    DZ: LocalizedString
    _text: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathNum2wordLocalesPt:
    BR: LocalizedString
    _text: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionModalsAdd_function:
    function_expression: LocalizedString
    function_expression_placeholder: LocalizedString
    function_name: LocalizedString
    function_name_placeholder: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionModalsChange_title:
    new_title: LocalizedString
    new_title_placeholder: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionModalsChange_x_label:
    new_label: LocalizedString
    new_label_placeholder: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionModalsChange_y_label:
    new_label: LocalizedString
    new_label_placeholder: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionModalsRename_function:
    new_name: LocalizedString
    new_name_placeholder: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionSelect_menusDerive:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionSelect_menusIntegrate:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionSelect_menusRename_function:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsMathPlotfunctionSelect_menusStyle:
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAutopublishErrorIs_already:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAutopublishErrorIs_not:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAutopublishErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityAutopublishErrorNot_news_channel:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBattlelogDescription:
    battleTime: LocalizedString
    battle_time: LocalizedString
    duration: LocalizedString
    enemies: LocalizedString
    enemy: LocalizedString
    gameMap: LocalizedString
    gameMode: LocalizedString
    game_map: LocalizedString
    game_mode: LocalizedString
    result: LocalizedString
    starPlayer: LocalizedString
    star_player: LocalizedString
    team1: LocalizedString
    team2: LocalizedString
    teamPlayer: LocalizedString
    trophyChange: LocalizedString
    trophy_change: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBattlelogError:
    notFound: CommandsUtilityBrawlstarsBattlelogErrorNotFound
    notLinked: CommandsUtilityBrawlstarsBattlelogErrorNotLinked
    userNotLinked: CommandsUtilityBrawlstarsBattlelogErrorUserNotLinked

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBrawlersDescription:
    gadget: LocalizedString
    gadgets: LocalizedString
    gear: LocalizedString
    gears: LocalizedString
    maxTier: LocalizedString
    overview: LocalizedString
    overviewMaxTier: LocalizedString
    starPower: LocalizedString
    starPowers: LocalizedString
    star_power: LocalizedString
    star_powers: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBrawlersError:
    notFound: CommandsUtilityBrawlstarsBrawlersErrorNotFound
    notLinked: CommandsUtilityBrawlstarsBrawlersErrorNotLinked

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBrawlersSearch:
    label: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString
    error: CommandsUtilityBrawlstarsBrawlersSearchError

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsClubDescription:
    member: LocalizedString
    overview: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsClubError:
    notFound: CommandsUtilityBrawlstarsClubErrorNotFound

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsClubSearch:
    label: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString
    error: CommandsUtilityBrawlstarsClubSearchError

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsEventsError:
    notFound: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsEventsNotFound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsLinkError:
    alreadyLinked: CommandsUtilityBrawlstarsLinkErrorAlreadyLinked
    notFound: CommandsUtilityBrawlstarsLinkErrorNotFound

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsLinkSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsPlayerinfoDescription:
    _3v3Victories: LocalizedString
    brawlers: LocalizedString
    club: LocalizedString
    duoVictories: LocalizedString
    expLevel: LocalizedString
    highestTrophies: LocalizedString
    highest_trophies: LocalizedString
    soloVictories: LocalizedString
    trophies: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsPlayerinfoError:
    notFound: CommandsUtilityBrawlstarsPlayerinfoErrorNotFound
    notLinked: CommandsUtilityBrawlstarsPlayerinfoErrorNotLinked

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsUnlinkError:
    notLinked: CommandsUtilityBrawlstarsUnlinkErrorNotLinked

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsUnlinkSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityFeedbackModalFeedbackdescription:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityFeedbackModalFeedbacktitle:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityFeedbackModalSubmitted:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityFeedbackModalTimeout:
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduledErrorNo_messages:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduledErrorNot_found:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityRemovescheduledErrorTimeout:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationError:
    missingBotPermissions: CommandsUtilityTwitchAddTwitchLiveNotificationErrorMissingBotPermissions
    missingPermissions: CommandsUtilityTwitchAddTwitchLiveNotificationErrorMissingPermissions
    twitchNameNotFound: CommandsUtilityTwitchAddTwitchLiveNotificationErrorTwitchNameNotFound

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationErrors:
    missingBotPermissions: CommandsUtilityTwitchAddTwitchLiveNotificationErrorsMissingBotPermissions
    missingPermissions: CommandsUtilityTwitchAddTwitchLiveNotificationErrorsMissingPermissions
    notYourNotification: CommandsUtilityTwitchAddTwitchLiveNotificationErrorsNotYourNotification
    twitchNameNotFound: CommandsUtilityTwitchAddTwitchLiveNotificationErrorsTwitchNameNotFound

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationSuccess:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchListTwitchLiveNotificationsError:
    missingPermissions: CommandsUtilityTwitchListTwitchLiveNotificationsErrorMissingPermissions
    noNotifications: CommandsUtilityTwitchListTwitchLiveNotificationsErrorNoNotifications
    notYourNotification: CommandsUtilityTwitchListTwitchLiveNotificationsErrorNotYourNotification

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureModalCaseSensitive:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureModalCase_sensitive:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureModalResponse:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureModalTrigger:
    label: LocalizedString
    placeholder: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureTriggerAddChannel:
    description: LocalizedString
    placeholder: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsAdminTrigger_messagesConfigureTriggerNoTriggerMessages:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_channelErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_channelErrorNo_pro:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_roleErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistAdd_userErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_channelErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_roleErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistRemove_userErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLevelBlacklistShowErrorNo_permission:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistAddParamsChannel:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsLogsBlacklistRemoveParamsChannel:
    description: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBattlelogErrorNotFound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBattlelogErrorNotLinked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBattlelogErrorUserNotLinked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBrawlersErrorNotFound:
    _text: LocalizedString
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBrawlersErrorNotLinked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsBrawlersSearchError:
    description: LocalizedString
    invalidInput: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsClubErrorNotFound:
    _text: LocalizedString
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsClubSearchError:
    description: LocalizedString
    invalidInput: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsLinkErrorAlreadyLinked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsLinkErrorNotFound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsPlayerinfoErrorNotFound:
    _text: LocalizedString
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsPlayerinfoErrorNotLinked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityBrawlstarsUnlinkErrorNotLinked:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationErrorMissingBotPermissions:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationErrorMissingPermissions:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationErrorTwitchNameNotFound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationErrorsMissingBotPermissions:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationErrorsMissingPermissions:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationErrorsNotYourNotification:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchAddTwitchLiveNotificationErrorsTwitchNameNotFound:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchListTwitchLiveNotificationsErrorMissingPermissions:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchListTwitchLiveNotificationsErrorNoNotifications:
    description: LocalizedString
    title: LocalizedString

@dataclass(frozen=True, slots=True)
class CommandsUtilityTwitchListTwitchLiveNotificationsErrorNotYourNotification:
    description: LocalizedString

def build_commands() -> Commands:
    _n_commands_admin_add_role_multipleSuccess = CommandsAdminAdd_roleMultipleSuccess(
        action=LocalizedString('commands.admin.add_role.multipleSuccess.action'),
    )
    _n_commands_admin_add_role = CommandsAdminAdd_role(
        multipleSuccess=_n_commands_admin_add_role_multipleSuccess,
    )
    _n_commands_admin_addrole_alreadyHasRole = CommandsAdminAddroleAlreadyHasRole(
        description=LocalizedString('commands.admin.addrole.alreadyHasRole.description'),
        title=LocalizedString('commands.admin.addrole.alreadyHasRole.title'),
    )
    _n_commands_admin_addrole_cancel = CommandsAdminAddroleCancel(
        label=LocalizedString('commands.admin.addrole.cancel.label'),
    )
    _n_commands_admin_addrole_confirm = CommandsAdminAddroleConfirm(
        label=LocalizedString('commands.admin.addrole.confirm.label'),
    )
    _n_commands_admin_addrole_managedRole = CommandsAdminAddroleManagedRole(
        description=LocalizedString('commands.admin.addrole.managedRole.description'),
        title=LocalizedString('commands.admin.addrole.managedRole.title'),
    )
    _n_commands_admin_addrole_missingPermission = CommandsAdminAddroleMissingPermission(
        description=LocalizedString('commands.admin.addrole.missingPermission.description'),
        title=LocalizedString('commands.admin.addrole.missingPermission.title'),
    )
    _n_commands_admin_addrole_missingPermissionBot = CommandsAdminAddroleMissingPermissionBot(
        description=LocalizedString('commands.admin.addrole.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.addrole.missingPermissionBot.title'),
    )
    _n_commands_admin_addrole_noRole = CommandsAdminAddroleNoRole(
        description=LocalizedString('commands.admin.addrole.noRole.description'),
        title=LocalizedString('commands.admin.addrole.noRole.title'),
    )
    _n_commands_admin_addrole_noUser = CommandsAdminAddroleNoUser(
        description=LocalizedString('commands.admin.addrole.noUser.description'),
        title=LocalizedString('commands.admin.addrole.noUser.title'),
    )
    _n_commands_admin_addrole_roleSelect = CommandsAdminAddroleRoleSelect(
        placeholder=LocalizedString('commands.admin.addrole.roleSelect.placeholder'),
    )
    _n_commands_admin_addrole_roleTooHigh = CommandsAdminAddroleRoleTooHigh(
        description=LocalizedString('commands.admin.addrole.roleTooHigh.description'),
        title=LocalizedString('commands.admin.addrole.roleTooHigh.title'),
    )
    _n_commands_admin_addrole_roleTooHighBot = CommandsAdminAddroleRoleTooHighBot(
        description=LocalizedString('commands.admin.addrole.roleTooHighBot.description'),
        title=LocalizedString('commands.admin.addrole.roleTooHighBot.title'),
    )
    _n_commands_admin_addrole_success = CommandsAdminAddroleSuccess(
        description=LocalizedString('commands.admin.addrole.success.description'),
        title=LocalizedString('commands.admin.addrole.success.title'),
    )
    _n_commands_admin_addrole_userSelect = CommandsAdminAddroleUserSelect(
        placeholder=LocalizedString('commands.admin.addrole.userSelect.placeholder'),
    )
    _n_commands_admin_addrole = CommandsAdminAddrole(
        alreadyHasRole=_n_commands_admin_addrole_alreadyHasRole,
        cancel=_n_commands_admin_addrole_cancel,
        cancelled=LocalizedString('commands.admin.addrole.cancelled'),
        confirm=_n_commands_admin_addrole_confirm,
        managedRole=_n_commands_admin_addrole_managedRole,
        missingPermission=_n_commands_admin_addrole_missingPermission,
        missingPermissionBot=_n_commands_admin_addrole_missingPermissionBot,
        multiplePrompt=LocalizedString('commands.admin.addrole.multiplePrompt'),
        multipleSuccess=LocalizedString('commands.admin.addrole.multipleSuccess'),
        noRole=_n_commands_admin_addrole_noRole,
        noSelection=LocalizedString('commands.admin.addrole.noSelection'),
        noUser=_n_commands_admin_addrole_noUser,
        roleSelect=_n_commands_admin_addrole_roleSelect,
        roleTooHigh=_n_commands_admin_addrole_roleTooHigh,
        roleTooHighBot=_n_commands_admin_addrole_roleTooHighBot,
        success=_n_commands_admin_addrole_success,
        userSelect=_n_commands_admin_addrole_userSelect,
    )
    _n_commands_admin_administration_benchmark_bot = CommandsAdminAdministrationBenchmark_bot(
        error=LocalizedString('commands.admin.administration.benchmark_bot.error'),
        starting=LocalizedString('commands.admin.administration.benchmark_bot.starting'),
        unavailable=LocalizedString('commands.admin.administration.benchmark_bot.unavailable'),
    )
    _n_commands_admin_administration_test_bot = CommandsAdminAdministrationTest_bot(
        all_completed=LocalizedString('commands.admin.administration.test_bot.all_completed'),
        current_test_cmds=LocalizedString('commands.admin.administration.test_bot.current_test_cmds'),
        current_test_db=LocalizedString('commands.admin.administration.test_bot.current_test_db'),
        current_test_ping=LocalizedString('commands.admin.administration.test_bot.current_test_ping'),
        error=LocalizedString('commands.admin.administration.test_bot.error'),
        starting=LocalizedString('commands.admin.administration.test_bot.starting'),
        tests_unavailable=LocalizedString('commands.admin.administration.test_bot.tests_unavailable'),
    )
    _n_commands_admin_administration_update = CommandsAdminAdministrationUpdate(
        connection_failed=LocalizedString('commands.admin.administration.update.connection_failed'),
        http_error=LocalizedString('commands.admin.administration.update.http_error'),
        updating=LocalizedString('commands.admin.administration.update.updating'),
    )
    _n_commands_admin_administration = CommandsAdminAdministration(
        benchmark_bot=_n_commands_admin_administration_benchmark_bot,
        bs_bot_info=LocalizedString('commands.admin.administration.bs_bot_info'),
        bs_download_failed=LocalizedString('commands.admin.administration.bs_download_failed'),
        bs_emoji_created=LocalizedString('commands.admin.administration.bs_emoji_created'),
        bs_emoji_failed=LocalizedString('commands.admin.administration.bs_emoji_failed'),
        console_check=LocalizedString('commands.admin.administration.console_check'),
        github_auth_test=LocalizedString('commands.admin.administration.github_auth_test'),
        me=LocalizedString('commands.admin.administration.me'),
        permission_list=LocalizedString('commands.admin.administration.permission_list'),
        permission_result=LocalizedString('commands.admin.administration.permission_result'),
        set_guild_locale=LocalizedString('commands.admin.administration.set_guild_locale'),
        situation_approved=LocalizedString('commands.admin.administration.situation_approved'),
        situation_creator_gone=LocalizedString('commands.admin.administration.situation_creator_gone'),
        situation_deleted=LocalizedString('commands.admin.administration.situation_deleted'),
        situation_not_found=LocalizedString('commands.admin.administration.situation_not_found'),
        test_bot=_n_commands_admin_administration_test_bot,
        update=_n_commands_admin_administration_update,
    )
    _n_commands_admin_ban_error = CommandsAdminBanError(
        description=LocalizedString('commands.admin.ban.error.description'),
        title=LocalizedString('commands.admin.ban.error.title'),
    )
    _n_commands_admin_ban_forbidden = CommandsAdminBanForbidden(
        description=LocalizedString('commands.admin.ban.forbidden.description'),
        title=LocalizedString('commands.admin.ban.forbidden.title'),
    )
    _n_commands_admin_ban_missingPermission = CommandsAdminBanMissingPermission(
        description=LocalizedString('commands.admin.ban.missingPermission.description'),
        title=LocalizedString('commands.admin.ban.missingPermission.title'),
    )
    _n_commands_admin_ban_missingPermissionBot = CommandsAdminBanMissingPermissionBot(
        description=LocalizedString('commands.admin.ban.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.ban.missingPermissionBot.title'),
    )
    _n_commands_admin_ban_success = CommandsAdminBanSuccess(
        description=LocalizedString('commands.admin.ban.success.description'),
        title=LocalizedString('commands.admin.ban.success.title'),
    )
    _n_commands_admin_ban_targetTooHigh = CommandsAdminBanTargetTooHigh(
        description=LocalizedString('commands.admin.ban.targetTooHigh.description'),
        title=LocalizedString('commands.admin.ban.targetTooHigh.title'),
    )
    _n_commands_admin_ban = CommandsAdminBan(
        error=_n_commands_admin_ban_error,
        forbidden=_n_commands_admin_ban_forbidden,
        missingPermission=_n_commands_admin_ban_missingPermission,
        missingPermissionBot=_n_commands_admin_ban_missingPermissionBot,
        noReasonProvided=LocalizedString('commands.admin.ban.noReasonProvided'),
        success=_n_commands_admin_ban_success,
        targetTooHigh=_n_commands_admin_ban_targetTooHigh,
    )
    _n_commands_admin_boosterRole_error = CommandsAdminBoosterRoleError(
        description=LocalizedString('commands.admin.boosterRole.error.description'),
        title=LocalizedString('commands.admin.boosterRole.error.title'),
    )
    _n_commands_admin_boosterRole_forbidden = CommandsAdminBoosterRoleForbidden(
        description=LocalizedString('commands.admin.boosterRole.forbidden.description'),
        title=LocalizedString('commands.admin.boosterRole.forbidden.title'),
    )
    _n_commands_admin_boosterRole_missingPermission = CommandsAdminBoosterRoleMissingPermission(
        description=LocalizedString('commands.admin.boosterRole.missingPermission.description'),
        title=LocalizedString('commands.admin.boosterRole.missingPermission.title'),
    )
    _n_commands_admin_boosterRole_missingPermissionBot = CommandsAdminBoosterRoleMissingPermissionBot(
        description=LocalizedString('commands.admin.boosterRole.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.boosterRole.missingPermissionBot.title'),
    )
    _n_commands_admin_boosterRole_roleRemoved = CommandsAdminBoosterRoleRoleRemoved(
        description=LocalizedString('commands.admin.boosterRole.roleRemoved.description'),
        title=LocalizedString('commands.admin.boosterRole.roleRemoved.title'),
    )
    _n_commands_admin_boosterRole_roleTooHighBot = CommandsAdminBoosterRoleRoleTooHighBot(
        description=LocalizedString('commands.admin.boosterRole.roleTooHighBot.description'),
        title=LocalizedString('commands.admin.boosterRole.roleTooHighBot.title'),
    )
    _n_commands_admin_boosterRole_success = CommandsAdminBoosterRoleSuccess(
        description=LocalizedString('commands.admin.boosterRole.success.description'),
        descriptionWarning=LocalizedString('commands.admin.boosterRole.success.descriptionWarning'),
        title=LocalizedString('commands.admin.boosterRole.success.title'),
    )
    _n_commands_admin_boosterRole_targetTooHigh = CommandsAdminBoosterRoleTargetTooHigh(
        description=LocalizedString('commands.admin.boosterRole.targetTooHigh.description'),
        title=LocalizedString('commands.admin.boosterRole.targetTooHigh.title'),
    )
    _n_commands_admin_boosterRole = CommandsAdminBoosterRole(
        error=_n_commands_admin_boosterRole_error,
        forbidden=_n_commands_admin_boosterRole_forbidden,
        missingPermission=_n_commands_admin_boosterRole_missingPermission,
        missingPermissionBot=_n_commands_admin_boosterRole_missingPermissionBot,
        roleRemoved=_n_commands_admin_boosterRole_roleRemoved,
        roleTooHighBot=_n_commands_admin_boosterRole_roleTooHighBot,
        success=_n_commands_admin_boosterRole_success,
        targetTooHigh=_n_commands_admin_boosterRole_targetTooHigh,
    )
    _n_commands_admin_channel_farewell_alreadySet = CommandsAdminChannelFarewellAlreadySet(
        description=LocalizedString('commands.admin.channel.farewell.alreadySet.description'),
        title=LocalizedString('commands.admin.channel.farewell.alreadySet.title'),
    )
    _n_commands_admin_channel_farewell_deleteSuccess = CommandsAdminChannelFarewellDeleteSuccess(
        description=LocalizedString('commands.admin.channel.farewell.deleteSuccess.description'),
        title=LocalizedString('commands.admin.channel.farewell.deleteSuccess.title'),
    )
    _n_commands_admin_channel_farewell_missingBotPermission = CommandsAdminChannelFarewellMissingBotPermission(
        description=LocalizedString('commands.admin.channel.farewell.missingBotPermission.description'),
        title=LocalizedString('commands.admin.channel.farewell.missingBotPermission.title'),
    )
    _n_commands_admin_channel_farewell_missingPermission = CommandsAdminChannelFarewellMissingPermission(
        description=LocalizedString('commands.admin.channel.farewell.missingPermission.description'),
        title=LocalizedString('commands.admin.channel.farewell.missingPermission.title'),
    )
    _n_commands_admin_channel_farewell_missingPro = CommandsAdminChannelFarewellMissingPro(
        description=LocalizedString('commands.admin.channel.farewell.missingPro.description'),
        title=LocalizedString('commands.admin.channel.farewell.missingPro.title'),
    )
    _n_commands_admin_channel_farewell_notSet = CommandsAdminChannelFarewellNotSet(
        description=LocalizedString('commands.admin.channel.farewell.notSet.description'),
        title=LocalizedString('commands.admin.channel.farewell.notSet.title'),
    )
    _n_commands_admin_channel_farewell_success = CommandsAdminChannelFarewellSuccess(
        description=LocalizedString('commands.admin.channel.farewell.success.description'),
        title=LocalizedString('commands.admin.channel.farewell.success.title'),
    )
    _n_commands_admin_channel_farewell = CommandsAdminChannelFarewell(
        alreadySet=_n_commands_admin_channel_farewell_alreadySet,
        defaultFarewellMessage=LocalizedString('commands.admin.channel.farewell.defaultFarewellMessage'),
        deleteSuccess=_n_commands_admin_channel_farewell_deleteSuccess,
        memberNumber=LocalizedString('commands.admin.channel.farewell.memberNumber'),
        missingBotPermission=_n_commands_admin_channel_farewell_missingBotPermission,
        missingPermission=_n_commands_admin_channel_farewell_missingPermission,
        missingPro=_n_commands_admin_channel_farewell_missingPro,
        notSet=_n_commands_admin_channel_farewell_notSet,
        success=_n_commands_admin_channel_farewell_success,
    )
    _n_commands_admin_channel_media_alreadySet = CommandsAdminChannelMediaAlreadySet(
        description=LocalizedString('commands.admin.channel.media.alreadySet.description'),
        title=LocalizedString('commands.admin.channel.media.alreadySet.title'),
    )
    _n_commands_admin_channel_media_deleteSuccess = CommandsAdminChannelMediaDeleteSuccess(
        description=LocalizedString('commands.admin.channel.media.deleteSuccess.description'),
        title=LocalizedString('commands.admin.channel.media.deleteSuccess.title'),
    )
    _n_commands_admin_channel_media_infoMessage = CommandsAdminChannelMediaInfoMessage(
        description=LocalizedString('commands.admin.channel.media.infoMessage.description'),
        title=LocalizedString('commands.admin.channel.media.infoMessage.title'),
    )
    _n_commands_admin_channel_media_infoMessageDelete = CommandsAdminChannelMediaInfoMessageDelete(
        description=LocalizedString('commands.admin.channel.media.infoMessageDelete.description'),
        title=LocalizedString('commands.admin.channel.media.infoMessageDelete.title'),
    )
    _n_commands_admin_channel_media_missingPermission = CommandsAdminChannelMediaMissingPermission(
        description=LocalizedString('commands.admin.channel.media.missingPermission.description'),
        title=LocalizedString('commands.admin.channel.media.missingPermission.title'),
    )
    _n_commands_admin_channel_media_missingPermissionBot = CommandsAdminChannelMediaMissingPermissionBot(
        description=LocalizedString('commands.admin.channel.media.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.channel.media.missingPermissionBot.title'),
    )
    _n_commands_admin_channel_media_notSet = CommandsAdminChannelMediaNotSet(
        description=LocalizedString('commands.admin.channel.media.notSet.description'),
        title=LocalizedString('commands.admin.channel.media.notSet.title'),
    )
    _n_commands_admin_channel_media_onlyMedia = CommandsAdminChannelMediaOnlyMedia(
        description=LocalizedString('commands.admin.channel.media.onlyMedia.description'),
        title=LocalizedString('commands.admin.channel.media.onlyMedia.title'),
    )
    _n_commands_admin_channel_media_optedOut = CommandsAdminChannelMediaOptedOut(
        description=LocalizedString('commands.admin.channel.media.optedOut.description'),
        title=LocalizedString('commands.admin.channel.media.optedOut.title'),
    )
    _n_commands_admin_channel_media_success = CommandsAdminChannelMediaSuccess(
        description=LocalizedString('commands.admin.channel.media.success.description'),
        title=LocalizedString('commands.admin.channel.media.success.title'),
    )
    _n_commands_admin_channel_media = CommandsAdminChannelMedia(
        alreadySet=_n_commands_admin_channel_media_alreadySet,
        deleteSuccess=_n_commands_admin_channel_media_deleteSuccess,
        infoMessage=_n_commands_admin_channel_media_infoMessage,
        infoMessageDelete=_n_commands_admin_channel_media_infoMessageDelete,
        missingPermission=_n_commands_admin_channel_media_missingPermission,
        missingPermissionBot=_n_commands_admin_channel_media_missingPermissionBot,
        notSet=_n_commands_admin_channel_media_notSet,
        onlyMedia=_n_commands_admin_channel_media_onlyMedia,
        optedOut=_n_commands_admin_channel_media_optedOut,
        success=_n_commands_admin_channel_media_success,
    )
    _n_commands_admin_channel_welcome_alreadySet = CommandsAdminChannelWelcomeAlreadySet(
        description=LocalizedString('commands.admin.channel.welcome.alreadySet.description'),
        title=LocalizedString('commands.admin.channel.welcome.alreadySet.title'),
    )
    _n_commands_admin_channel_welcome_deleteSuccess = CommandsAdminChannelWelcomeDeleteSuccess(
        description=LocalizedString('commands.admin.channel.welcome.deleteSuccess.description'),
        title=LocalizedString('commands.admin.channel.welcome.deleteSuccess.title'),
    )
    _n_commands_admin_channel_welcome_missingBotPermission = CommandsAdminChannelWelcomeMissingBotPermission(
        description=LocalizedString('commands.admin.channel.welcome.missingBotPermission.description'),
        title=LocalizedString('commands.admin.channel.welcome.missingBotPermission.title'),
    )
    _n_commands_admin_channel_welcome_missingPermission = CommandsAdminChannelWelcomeMissingPermission(
        description=LocalizedString('commands.admin.channel.welcome.missingPermission.description'),
        title=LocalizedString('commands.admin.channel.welcome.missingPermission.title'),
    )
    _n_commands_admin_channel_welcome_missingPro = CommandsAdminChannelWelcomeMissingPro(
        description=LocalizedString('commands.admin.channel.welcome.missingPro.description'),
        title=LocalizedString('commands.admin.channel.welcome.missingPro.title'),
    )
    _n_commands_admin_channel_welcome_notSet = CommandsAdminChannelWelcomeNotSet(
        description=LocalizedString('commands.admin.channel.welcome.notSet.description'),
        title=LocalizedString('commands.admin.channel.welcome.notSet.title'),
    )
    _n_commands_admin_channel_welcome_success = CommandsAdminChannelWelcomeSuccess(
        description=LocalizedString('commands.admin.channel.welcome.success.description'),
        title=LocalizedString('commands.admin.channel.welcome.success.title'),
    )
    _n_commands_admin_channel_welcome = CommandsAdminChannelWelcome(
        alreadySet=_n_commands_admin_channel_welcome_alreadySet,
        defaultWelcomeMessage=LocalizedString('commands.admin.channel.welcome.defaultWelcomeMessage'),
        deleteSuccess=_n_commands_admin_channel_welcome_deleteSuccess,
        memberNumber=LocalizedString('commands.admin.channel.welcome.memberNumber'),
        missingBotPermission=_n_commands_admin_channel_welcome_missingBotPermission,
        missingPermission=_n_commands_admin_channel_welcome_missingPermission,
        missingPro=_n_commands_admin_channel_welcome_missingPro,
        notSet=_n_commands_admin_channel_welcome_notSet,
        success=_n_commands_admin_channel_welcome_success,
    )
    _n_commands_admin_channel = CommandsAdminChannel(
        farewell=_n_commands_admin_channel_farewell,
        media=_n_commands_admin_channel_media,
        welcome=_n_commands_admin_channel_welcome,
    )
    _n_commands_admin_close_ticket_button = CommandsAdminClose_ticketButton(
        label=LocalizedString('commands.admin.close_ticket.button.label'),
    )
    _n_commands_admin_close_ticket_error = CommandsAdminClose_ticketError(
        ticketNotFound1=LocalizedString('commands.admin.close_ticket.error.ticketNotFound1'),
        ticketNotFound2=LocalizedString('commands.admin.close_ticket.error.ticketNotFound2'),
        ticketNotFound3=LocalizedString('commands.admin.close_ticket.error.ticketNotFound3'),
    )
    _n_commands_admin_close_ticket_success = CommandsAdminClose_ticketSuccess(
        description=LocalizedString('commands.admin.close_ticket.success.description'),
        ticketClosed=LocalizedString('commands.admin.close_ticket.success.ticketClosed'),
        ticketClosedDescription=LocalizedString('commands.admin.close_ticket.success.ticketClosedDescription'),
        title=LocalizedString('commands.admin.close_ticket.success.title'),
        viewOnlineSummary=LocalizedString('commands.admin.close_ticket.success.viewOnlineSummary'),
        viewThread=LocalizedString('commands.admin.close_ticket.success.viewThread'),
    )
    _n_commands_admin_close_ticket = CommandsAdminClose_ticket(
        button=_n_commands_admin_close_ticket_button,
        error=_n_commands_admin_close_ticket_error,
        success=_n_commands_admin_close_ticket_success,
    )
    _n_commands_admin_copy7tv_addModal_success = CommandsAdminCopy7tvAddModalSuccess(
        description=LocalizedString('commands.admin.copy7tv.addModal.success.description'),
        title=LocalizedString('commands.admin.copy7tv.addModal.success.title'),
    )
    _n_commands_admin_copy7tv_addModal = CommandsAdminCopy7tvAddModal(
        downloadError=LocalizedString('commands.admin.copy7tv.addModal.downloadError'),
        error=LocalizedString('commands.admin.copy7tv.addModal.error'),
        invalidNumber=LocalizedString('commands.admin.copy7tv.addModal.invalidNumber'),
        label=LocalizedString('commands.admin.copy7tv.addModal.label'),
        limitAnimated=LocalizedString('commands.admin.copy7tv.addModal.limitAnimated'),
        limitStatic=LocalizedString('commands.admin.copy7tv.addModal.limitStatic'),
        placeholder=LocalizedString('commands.admin.copy7tv.addModal.placeholder'),
        reason=LocalizedString('commands.admin.copy7tv.addModal.reason'),
        success=_n_commands_admin_copy7tv_addModal_success,
        title=LocalizedString('commands.admin.copy7tv.addModal.title'),
    )
    _n_commands_admin_copy7tv_error_notFound = CommandsAdminCopy7tvErrorNotFound(
        description=LocalizedString('commands.admin.copy7tv.error.notFound.description'),
        title=LocalizedString('commands.admin.copy7tv.error.notFound.title'),
    )
    _n_commands_admin_copy7tv_error = CommandsAdminCopy7tvError(
        notFound=_n_commands_admin_copy7tv_error_notFound,
    )
    _n_commands_admin_copy7tv_missingPermission = CommandsAdminCopy7tvMissingPermission(
        description=LocalizedString('commands.admin.copy7tv.missingPermission.description'),
        title=LocalizedString('commands.admin.copy7tv.missingPermission.title'),
    )
    _n_commands_admin_copy7tv_missingPermissionBot = CommandsAdminCopy7tvMissingPermissionBot(
        description=LocalizedString('commands.admin.copy7tv.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.copy7tv.missingPermissionBot.title'),
    )
    _n_commands_admin_copy7tv = CommandsAdminCopy7tv(
        addModal=_n_commands_admin_copy7tv_addModal,
        error=_n_commands_admin_copy7tv_error,
        footer=LocalizedString('commands.admin.copy7tv.footer'),
        missingPermission=_n_commands_admin_copy7tv_missingPermission,
        missingPermissionBot=_n_commands_admin_copy7tv_missingPermissionBot,
        noEmotes=LocalizedString('commands.admin.copy7tv.noEmotes'),
        notYourEmbed=LocalizedString('commands.admin.copy7tv.notYourEmbed'),
        title=LocalizedString('commands.admin.copy7tv.title'),
    )
    _n_commands_admin_copyEmoji_error_limitReached = CommandsAdminCopyEmojiErrorLimitReached(
        description=LocalizedString('commands.admin.copyEmoji.error.limitReached.description'),
        title=LocalizedString('commands.admin.copyEmoji.error.limitReached.title'),
    )
    _n_commands_admin_copyEmoji_error_noEmojis = CommandsAdminCopyEmojiErrorNoEmojis(
        description=LocalizedString('commands.admin.copyEmoji.error.noEmojis.description'),
        title=LocalizedString('commands.admin.copyEmoji.error.noEmojis.title'),
    )
    _n_commands_admin_copyEmoji_error_proRequired = CommandsAdminCopyEmojiErrorProRequired(
        description=LocalizedString('commands.admin.copyEmoji.error.proRequired.description'),
        title=LocalizedString('commands.admin.copyEmoji.error.proRequired.title'),
    )
    _n_commands_admin_copyEmoji_error = CommandsAdminCopyEmojiError(
        description=LocalizedString('commands.admin.copyEmoji.error.description'),
        limitReached=_n_commands_admin_copyEmoji_error_limitReached,
        noEmojis=_n_commands_admin_copyEmoji_error_noEmojis,
        proRequired=_n_commands_admin_copyEmoji_error_proRequired,
        title=LocalizedString('commands.admin.copyEmoji.error.title'),
    )
    _n_commands_admin_copyEmoji_missingPermission = CommandsAdminCopyEmojiMissingPermission(
        description=LocalizedString('commands.admin.copyEmoji.missingPermission.description'),
        title=LocalizedString('commands.admin.copyEmoji.missingPermission.title'),
    )
    _n_commands_admin_copyEmoji_missingPermissionBot = CommandsAdminCopyEmojiMissingPermissionBot(
        description=LocalizedString('commands.admin.copyEmoji.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.copyEmoji.missingPermissionBot.title'),
    )
    _n_commands_admin_copyEmoji_partialSuccess = CommandsAdminCopyEmojiPartialSuccess(
        description=LocalizedString('commands.admin.copyEmoji.partialSuccess.description'),
        title=LocalizedString('commands.admin.copyEmoji.partialSuccess.title'),
    )
    _n_commands_admin_copyEmoji_success_multiple = CommandsAdminCopyEmojiSuccessMultiple(
        description=LocalizedString('commands.admin.copyEmoji.success.multiple.description'),
        title=LocalizedString('commands.admin.copyEmoji.success.multiple.title'),
    )
    _n_commands_admin_copyEmoji_success = CommandsAdminCopyEmojiSuccess(
        description=LocalizedString('commands.admin.copyEmoji.success.description'),
        multiple=_n_commands_admin_copyEmoji_success_multiple,
        title=LocalizedString('commands.admin.copyEmoji.success.title'),
    )
    _n_commands_admin_copyEmoji = CommandsAdminCopyEmoji(
        error=_n_commands_admin_copyEmoji_error,
        missingPermission=_n_commands_admin_copyEmoji_missingPermission,
        missingPermissionBot=_n_commands_admin_copyEmoji_missingPermissionBot,
        partialSuccess=_n_commands_admin_copyEmoji_partialSuccess,
        reason=LocalizedString('commands.admin.copyEmoji.reason'),
        success=_n_commands_admin_copyEmoji_success,
    )
    _n_commands_admin_copyrole_missingPermission = CommandsAdminCopyroleMissingPermission(
        description=LocalizedString('commands.admin.copyrole.missingPermission.description'),
        title=LocalizedString('commands.admin.copyrole.missingPermission.title'),
    )
    _n_commands_admin_copyrole_missingPermissionBot = CommandsAdminCopyroleMissingPermissionBot(
        description=LocalizedString('commands.admin.copyrole.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.copyrole.missingPermissionBot.title'),
    )
    _n_commands_admin_copyrole_success = CommandsAdminCopyroleSuccess(
        description=LocalizedString('commands.admin.copyrole.success.description'),
        title=LocalizedString('commands.admin.copyrole.success.title'),
    )
    _n_commands_admin_copyrole = CommandsAdminCopyrole(
        missingPermission=_n_commands_admin_copyrole_missingPermission,
        missingPermissionBot=_n_commands_admin_copyrole_missingPermissionBot,
        reason=LocalizedString('commands.admin.copyrole.reason'),
        success=_n_commands_admin_copyrole_success,
    )
    _n_commands_admin_createEmoji_missingPermission = CommandsAdminCreateEmojiMissingPermission(
        description=LocalizedString('commands.admin.createEmoji.missingPermission.description'),
        title=LocalizedString('commands.admin.createEmoji.missingPermission.title'),
    )
    _n_commands_admin_createEmoji_success = CommandsAdminCreateEmojiSuccess(
        description=LocalizedString('commands.admin.createEmoji.success.description'),
        title=LocalizedString('commands.admin.createEmoji.success.title'),
    )
    _n_commands_admin_createEmoji = CommandsAdminCreateEmoji(
        allRoles=LocalizedString('commands.admin.createEmoji.allRoles'),
        error=LocalizedString('commands.admin.createEmoji.error'),
        imageDownloadError=LocalizedString('commands.admin.createEmoji.imageDownloadError'),
        missingPermission=_n_commands_admin_createEmoji_missingPermission,
        roleSelect=LocalizedString('commands.admin.createEmoji.roleSelect'),
        roleSelectPlaceholder=LocalizedString('commands.admin.createEmoji.roleSelectPlaceholder'),
        role_select=LocalizedString('commands.admin.createEmoji.role_select'),
        role_selectPlaceholder=LocalizedString('commands.admin.createEmoji.role_selectPlaceholder'),
        success=_n_commands_admin_createEmoji_success,
    )
    _n_commands_admin_create_ticket_button = CommandsAdminCreate_ticketButton(
        label=LocalizedString('commands.admin.create_ticket.button.label'),
    )
    _n_commands_admin_create_ticket_embed = CommandsAdminCreate_ticketEmbed(
        description=LocalizedString('commands.admin.create_ticket.embed.description'),
        title=LocalizedString('commands.admin.create_ticket.embed.title'),
    )
    _n_commands_admin_create_ticket_error = CommandsAdminCreate_ticketError(
        description=LocalizedString('commands.admin.create_ticket.error.description'),
        title=LocalizedString('commands.admin.create_ticket.error.title'),
    )
    _n_commands_admin_create_ticket_missingBotPermission = CommandsAdminCreate_ticketMissingBotPermission(
        description=LocalizedString('commands.admin.create_ticket.missingBotPermission.description'),
        title=LocalizedString('commands.admin.create_ticket.missingBotPermission.title'),
    )
    _n_commands_admin_create_ticket_missingPermission = CommandsAdminCreate_ticketMissingPermission(
        description=LocalizedString('commands.admin.create_ticket.missingPermission.description'),
        title=LocalizedString('commands.admin.create_ticket.missingPermission.title'),
    )
    _n_commands_admin_create_ticket_success = CommandsAdminCreate_ticketSuccess(
        description=LocalizedString('commands.admin.create_ticket.success.description'),
        title=LocalizedString('commands.admin.create_ticket.success.title'),
    )
    _n_commands_admin_create_ticket = CommandsAdminCreate_ticket(
        button=_n_commands_admin_create_ticket_button,
        embed=_n_commands_admin_create_ticket_embed,
        error=_n_commands_admin_create_ticket_error,
        missingBotPermission=_n_commands_admin_create_ticket_missingBotPermission,
        missingPermission=_n_commands_admin_create_ticket_missingPermission,
        success=_n_commands_admin_create_ticket_success,
    )
    _n_commands_admin_createrole_forbidden = CommandsAdminCreateroleForbidden(
        description=LocalizedString('commands.admin.createrole.forbidden.description'),
        title=LocalizedString('commands.admin.createrole.forbidden.title'),
    )
    _n_commands_admin_createrole_http_error = CommandsAdminCreateroleHttp_error(
        description=LocalizedString('commands.admin.createrole.http_error.description'),
        title=LocalizedString('commands.admin.createrole.http_error.title'),
    )
    _n_commands_admin_createrole_iconTooLarge = CommandsAdminCreateroleIconTooLarge(
        description=LocalizedString('commands.admin.createrole.iconTooLarge.description'),
        title=LocalizedString('commands.admin.createrole.iconTooLarge.title'),
    )
    _n_commands_admin_createrole_invalidColor = CommandsAdminCreateroleInvalidColor(
        description=LocalizedString('commands.admin.createrole.invalidColor.description'),
        title=LocalizedString('commands.admin.createrole.invalidColor.title'),
    )
    _n_commands_admin_createrole_invalidIcon = CommandsAdminCreateroleInvalidIcon(
        description=LocalizedString('commands.admin.createrole.invalidIcon.description'),
        title=LocalizedString('commands.admin.createrole.invalidIcon.title'),
    )
    _n_commands_admin_createrole_missingName = CommandsAdminCreateroleMissingName(
        description=LocalizedString('commands.admin.createrole.missingName.description'),
        title=LocalizedString('commands.admin.createrole.missingName.title'),
    )
    _n_commands_admin_createrole_missingPermission = CommandsAdminCreateroleMissingPermission(
        description=LocalizedString('commands.admin.createrole.missingPermission.description'),
        title=LocalizedString('commands.admin.createrole.missingPermission.title'),
    )
    _n_commands_admin_createrole_missingPermissionBot = CommandsAdminCreateroleMissingPermissionBot(
        description=LocalizedString('commands.admin.createrole.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.createrole.missingPermissionBot.title'),
    )
    _n_commands_admin_createrole_nameTooLong = CommandsAdminCreateroleNameTooLong(
        description=LocalizedString('commands.admin.createrole.nameTooLong.description'),
        title=LocalizedString('commands.admin.createrole.nameTooLong.title'),
    )
    _n_commands_admin_createrole_notfound = CommandsAdminCreateroleNotfound(
        description=LocalizedString('commands.admin.createrole.notfound.description'),
        title=LocalizedString('commands.admin.createrole.notfound.title'),
    )
    _n_commands_admin_createrole_reasonTooLong = CommandsAdminCreateroleReasonTooLong(
        description=LocalizedString('commands.admin.createrole.reasonTooLong.description'),
        title=LocalizedString('commands.admin.createrole.reasonTooLong.title'),
    )
    _n_commands_admin_createrole_roleIconsNotEnabled = CommandsAdminCreateroleRoleIconsNotEnabled(
        description=LocalizedString('commands.admin.createrole.roleIconsNotEnabled.description'),
        title=LocalizedString('commands.admin.createrole.roleIconsNotEnabled.title'),
    )
    _n_commands_admin_createrole_success = CommandsAdminCreateroleSuccess(
        description=LocalizedString('commands.admin.createrole.success.description'),
        title=LocalizedString('commands.admin.createrole.success.title'),
    )
    _n_commands_admin_createrole = CommandsAdminCreaterole(
        forbidden=_n_commands_admin_createrole_forbidden,
        http_error=_n_commands_admin_createrole_http_error,
        iconTooLarge=_n_commands_admin_createrole_iconTooLarge,
        invalidColor=_n_commands_admin_createrole_invalidColor,
        invalidIcon=_n_commands_admin_createrole_invalidIcon,
        missingName=_n_commands_admin_createrole_missingName,
        missingPermission=_n_commands_admin_createrole_missingPermission,
        missingPermissionBot=_n_commands_admin_createrole_missingPermissionBot,
        nameTooLong=_n_commands_admin_createrole_nameTooLong,
        notfound=_n_commands_admin_createrole_notfound,
        reasonTooLong=_n_commands_admin_createrole_reasonTooLong,
        roleIconsNotEnabled=_n_commands_admin_createrole_roleIconsNotEnabled,
        success=_n_commands_admin_createrole_success,
    )
    _n_commands_admin_database_sync = CommandsAdminDatabase_sync(
        aborted=LocalizedString('commands.admin.database_sync.aborted'),
        analyzing=LocalizedString('commands.admin.database_sync.analyzing'),
        backup_error=LocalizedString('commands.admin.database_sync.backup_error'),
        backup_success=LocalizedString('commands.admin.database_sync.backup_success'),
        cancel_token=LocalizedString('commands.admin.database_sync.cancel_token'),
        download_error=LocalizedString('commands.admin.database_sync.download_error'),
        download_failed=LocalizedString('commands.admin.database_sync.download_failed'),
        downloading=LocalizedString('commands.admin.database_sync.downloading'),
        filter_error=LocalizedString('commands.admin.database_sync.filter_error'),
        import_error=LocalizedString('commands.admin.database_sync.import_error'),
        importing=LocalizedString('commands.admin.database_sync.importing'),
        no_attachment=LocalizedString('commands.admin.database_sync.no_attachment'),
        no_schema_found=LocalizedString('commands.admin.database_sync.no_schema_found'),
        preparing_import=LocalizedString('commands.admin.database_sync.preparing_import'),
        schema_prompt=LocalizedString('commands.admin.database_sync.schema_prompt'),
        schema_warning=LocalizedString('commands.admin.database_sync.schema_warning'),
        success=LocalizedString('commands.admin.database_sync.success'),
        timeout=LocalizedString('commands.admin.database_sync.timeout'),
    )
    _n_commands_admin_deleterole_forbidden = CommandsAdminDeleteroleForbidden(
        description=LocalizedString('commands.admin.deleterole.forbidden.description'),
        title=LocalizedString('commands.admin.deleterole.forbidden.title'),
    )
    _n_commands_admin_deleterole_http_error = CommandsAdminDeleteroleHttp_error(
        description=LocalizedString('commands.admin.deleterole.http_error.description'),
        title=LocalizedString('commands.admin.deleterole.http_error.title'),
    )
    _n_commands_admin_deleterole_missingPermission = CommandsAdminDeleteroleMissingPermission(
        description=LocalizedString('commands.admin.deleterole.missingPermission.description'),
        title=LocalizedString('commands.admin.deleterole.missingPermission.title'),
    )
    _n_commands_admin_deleterole_missingPermissionBot = CommandsAdminDeleteroleMissingPermissionBot(
        description=LocalizedString('commands.admin.deleterole.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.deleterole.missingPermissionBot.title'),
    )
    _n_commands_admin_deleterole_notfound = CommandsAdminDeleteroleNotfound(
        description=LocalizedString('commands.admin.deleterole.notfound.description'),
        title=LocalizedString('commands.admin.deleterole.notfound.title'),
    )
    _n_commands_admin_deleterole_roleTooHigh = CommandsAdminDeleteroleRoleTooHigh(
        description=LocalizedString('commands.admin.deleterole.roleTooHigh.description'),
        title=LocalizedString('commands.admin.deleterole.roleTooHigh.title'),
    )
    _n_commands_admin_deleterole_roleTooHighBot = CommandsAdminDeleteroleRoleTooHighBot(
        description=LocalizedString('commands.admin.deleterole.roleTooHighBot.description'),
        title=LocalizedString('commands.admin.deleterole.roleTooHighBot.title'),
    )
    _n_commands_admin_deleterole_success = CommandsAdminDeleteroleSuccess(
        description=LocalizedString('commands.admin.deleterole.success.description'),
        title=LocalizedString('commands.admin.deleterole.success.title'),
    )
    _n_commands_admin_deleterole = CommandsAdminDeleterole(
        forbidden=_n_commands_admin_deleterole_forbidden,
        http_error=_n_commands_admin_deleterole_http_error,
        missingPermission=_n_commands_admin_deleterole_missingPermission,
        missingPermissionBot=_n_commands_admin_deleterole_missingPermissionBot,
        noRole=LocalizedString('commands.admin.deleterole.noRole'),
        notfound=_n_commands_admin_deleterole_notfound,
        roleTooHigh=_n_commands_admin_deleterole_roleTooHigh,
        roleTooHighBot=_n_commands_admin_deleterole_roleTooHighBot,
        success=_n_commands_admin_deleterole_success,
    )
    _n_commands_admin_demo_message = CommandsAdminDemo_message(
        confirm=LocalizedString('commands.admin.demo_message.confirm'),
    )
    _n_commands_admin_embed_buttons = CommandsAdminEmbedButtons(
        addField=LocalizedString('commands.admin.embed.buttons.addField'),
        editField=LocalizedString('commands.admin.embed.buttons.editField'),
        preview=LocalizedString('commands.admin.embed.buttons.preview'),
        removeField=LocalizedString('commands.admin.embed.buttons.removeField'),
        send=LocalizedString('commands.admin.embed.buttons.send'),
        setColor=LocalizedString('commands.admin.embed.buttons.setColor'),
        setDescription=LocalizedString('commands.admin.embed.buttons.setDescription'),
        setFooter=LocalizedString('commands.admin.embed.buttons.setFooter'),
        setImage=LocalizedString('commands.admin.embed.buttons.setImage'),
        setThumbnail=LocalizedString('commands.admin.embed.buttons.setThumbnail'),
        setTitle=LocalizedString('commands.admin.embed.buttons.setTitle'),
    )
    _n_commands_admin_embed_missingPermission = CommandsAdminEmbedMissingPermission(
        description=LocalizedString('commands.admin.embed.missingPermission.description'),
        title=LocalizedString('commands.admin.embed.missingPermission.title'),
    )
    _n_commands_admin_embed_missingTitle = CommandsAdminEmbedMissingTitle(
        description=LocalizedString('commands.admin.embed.missingTitle.description'),
        title=LocalizedString('commands.admin.embed.missingTitle.title'),
    )
    _n_commands_admin_embed_modals_colorModal = CommandsAdminEmbedModalsColorModal(
        label=LocalizedString('commands.admin.embed.modals.colorModal.label'),
        title=LocalizedString('commands.admin.embed.modals.colorModal.title'),
    )
    _n_commands_admin_embed_modals_editFieldModal = CommandsAdminEmbedModalsEditFieldModal(
        fieldLabel=LocalizedString('commands.admin.embed.modals.editFieldModal.fieldLabel'),
        selectField=LocalizedString('commands.admin.embed.modals.editFieldModal.selectField'),
        title=LocalizedString('commands.admin.embed.modals.editFieldModal.title'),
    )
    _n_commands_admin_embed_modals_fieldModal = CommandsAdminEmbedModalsFieldModal(
        inlineLabel=LocalizedString('commands.admin.embed.modals.fieldModal.inlineLabel'),
        nameLabel=LocalizedString('commands.admin.embed.modals.fieldModal.nameLabel'),
        title=LocalizedString('commands.admin.embed.modals.fieldModal.title'),
        valueLabel=LocalizedString('commands.admin.embed.modals.fieldModal.valueLabel'),
    )
    _n_commands_admin_embed_modals_footerModal = CommandsAdminEmbedModalsFooterModal(
        iconLabel=LocalizedString('commands.admin.embed.modals.footerModal.iconLabel'),
        label=LocalizedString('commands.admin.embed.modals.footerModal.label'),
        title=LocalizedString('commands.admin.embed.modals.footerModal.title'),
    )
    _n_commands_admin_embed_modals_imageModal = CommandsAdminEmbedModalsImageModal(
        label=LocalizedString('commands.admin.embed.modals.imageModal.label'),
        title=LocalizedString('commands.admin.embed.modals.imageModal.title'),
    )
    _n_commands_admin_embed_modals_removeFieldModal = CommandsAdminEmbedModalsRemoveFieldModal(
        fieldLabel=LocalizedString('commands.admin.embed.modals.removeFieldModal.fieldLabel'),
        selectField=LocalizedString('commands.admin.embed.modals.removeFieldModal.selectField'),
        title=LocalizedString('commands.admin.embed.modals.removeFieldModal.title'),
    )
    _n_commands_admin_embed_modals_thumbnailModal = CommandsAdminEmbedModalsThumbnailModal(
        label=LocalizedString('commands.admin.embed.modals.thumbnailModal.label'),
        title=LocalizedString('commands.admin.embed.modals.thumbnailModal.title'),
    )
    _n_commands_admin_embed_modals_titleModal = CommandsAdminEmbedModalsTitleModal(
        label=LocalizedString('commands.admin.embed.modals.titleModal.label'),
        title=LocalizedString('commands.admin.embed.modals.titleModal.title'),
        urlLabel=LocalizedString('commands.admin.embed.modals.titleModal.urlLabel'),
    )
    _n_commands_admin_embed_modals = CommandsAdminEmbedModals(
        colorModal=_n_commands_admin_embed_modals_colorModal,
        editFieldModal=_n_commands_admin_embed_modals_editFieldModal,
        fieldModal=_n_commands_admin_embed_modals_fieldModal,
        footerModal=_n_commands_admin_embed_modals_footerModal,
        imageModal=_n_commands_admin_embed_modals_imageModal,
        removeFieldModal=_n_commands_admin_embed_modals_removeFieldModal,
        thumbnailModal=_n_commands_admin_embed_modals_thumbnailModal,
        titleModal=_n_commands_admin_embed_modals_titleModal,
    )
    _n_commands_admin_embed_setDescription = CommandsAdminEmbedSetDescription(
        descriptionUpdated=LocalizedString('commands.admin.embed.setDescription.descriptionUpdated'),
        message=LocalizedString('commands.admin.embed.setDescription.message'),
        timeout=LocalizedString('commands.admin.embed.setDescription.timeout'),
    )
    _n_commands_admin_embed = CommandsAdminEmbed(
        buttons=_n_commands_admin_embed_buttons,
        colorUpdated=LocalizedString('commands.admin.embed.colorUpdated'),
        creatorDescription=LocalizedString('commands.admin.embed.creatorDescription'),
        creatorTitle=LocalizedString('commands.admin.embed.creatorTitle'),
        descriptionUpdated=LocalizedString('commands.admin.embed.descriptionUpdated'),
        embedSent=LocalizedString('commands.admin.embed.embedSent'),
        fieldAdded=LocalizedString('commands.admin.embed.fieldAdded'),
        fieldEdited=LocalizedString('commands.admin.embed.fieldEdited'),
        fieldRemoved=LocalizedString('commands.admin.embed.fieldRemoved'),
        footerUpdated=LocalizedString('commands.admin.embed.footerUpdated'),
        imageUpdated=LocalizedString('commands.admin.embed.imageUpdated'),
        invalidColorCode=LocalizedString('commands.admin.embed.invalidColorCode'),
        maxFieldsReached=LocalizedString('commands.admin.embed.maxFieldsReached'),
        missingPermission=_n_commands_admin_embed_missingPermission,
        missingTitle=_n_commands_admin_embed_missingTitle,
        modals=_n_commands_admin_embed_modals,
        noFieldsToEdit=LocalizedString('commands.admin.embed.noFieldsToEdit'),
        noFieldsToRemove=LocalizedString('commands.admin.embed.noFieldsToRemove'),
        previewSent=LocalizedString('commands.admin.embed.previewSent'),
        setDescription=_n_commands_admin_embed_setDescription,
        thumbnailUpdated=LocalizedString('commands.admin.embed.thumbnailUpdated'),
        titleUpdated=LocalizedString('commands.admin.embed.titleUpdated'),
        unauthorizedUser=LocalizedString('commands.admin.embed.unauthorizedUser'),
    )
    _n_commands_admin_feedback = CommandsAdminFeedback(
        added=LocalizedString('commands.admin.feedback.added'),
        blocked=LocalizedString('commands.admin.feedback.blocked'),
        unblocked=LocalizedString('commands.admin.feedback.unblocked'),
    )
    _n_commands_admin_joinToCreateListener_channelDeleted = CommandsAdminJoinToCreateListenerChannelDeleted(
        description=LocalizedString('commands.admin.joinToCreateListener.channelDeleted.description'),
        title=LocalizedString('commands.admin.joinToCreateListener.channelDeleted.title'),
    )
    _n_commands_admin_joinToCreateListener_success = CommandsAdminJoinToCreateListenerSuccess(
        description=LocalizedString('commands.admin.joinToCreateListener.success.description'),
        title=LocalizedString('commands.admin.joinToCreateListener.success.title'),
    )
    _n_commands_admin_joinToCreateListener = CommandsAdminJoinToCreateListener(
        channelDeleted=_n_commands_admin_joinToCreateListener_channelDeleted,
        success=_n_commands_admin_joinToCreateListener_success,
    )
    _n_commands_admin_jointocreatechannel_alreadySet = CommandsAdminJointocreatechannelAlreadySet(
        description=LocalizedString('commands.admin.jointocreatechannel.alreadySet.description'),
        title=LocalizedString('commands.admin.jointocreatechannel.alreadySet.title'),
    )
    _n_commands_admin_jointocreatechannel_missingPermission = CommandsAdminJointocreatechannelMissingPermission(
        description=LocalizedString('commands.admin.jointocreatechannel.missingPermission.description'),
        title=LocalizedString('commands.admin.jointocreatechannel.missingPermission.title'),
    )
    _n_commands_admin_jointocreatechannel_success = CommandsAdminJointocreatechannelSuccess(
        description=LocalizedString('commands.admin.jointocreatechannel.success.description'),
        title=LocalizedString('commands.admin.jointocreatechannel.success.title'),
    )
    _n_commands_admin_jointocreatechannel = CommandsAdminJointocreatechannel(
        alreadySet=_n_commands_admin_jointocreatechannel_alreadySet,
        missingPermission=_n_commands_admin_jointocreatechannel_missingPermission,
        success=_n_commands_admin_jointocreatechannel_success,
    )
    _n_commands_admin_kick_error = CommandsAdminKickError(
        description=LocalizedString('commands.admin.kick.error.description'),
        title=LocalizedString('commands.admin.kick.error.title'),
    )
    _n_commands_admin_kick_forbidden = CommandsAdminKickForbidden(
        description=LocalizedString('commands.admin.kick.forbidden.description'),
        title=LocalizedString('commands.admin.kick.forbidden.title'),
    )
    _n_commands_admin_kick_missingPermission = CommandsAdminKickMissingPermission(
        description=LocalizedString('commands.admin.kick.missingPermission.description'),
        title=LocalizedString('commands.admin.kick.missingPermission.title'),
    )
    _n_commands_admin_kick_missingPermissionBot = CommandsAdminKickMissingPermissionBot(
        description=LocalizedString('commands.admin.kick.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.kick.missingPermissionBot.title'),
    )
    _n_commands_admin_kick_success = CommandsAdminKickSuccess(
        description=LocalizedString('commands.admin.kick.success.description'),
        title=LocalizedString('commands.admin.kick.success.title'),
    )
    _n_commands_admin_kick_targetTooHigh = CommandsAdminKickTargetTooHigh(
        description=LocalizedString('commands.admin.kick.targetTooHigh.description'),
        title=LocalizedString('commands.admin.kick.targetTooHigh.title'),
    )
    _n_commands_admin_kick = CommandsAdminKick(
        error=_n_commands_admin_kick_error,
        forbidden=_n_commands_admin_kick_forbidden,
        missingPermission=_n_commands_admin_kick_missingPermission,
        missingPermissionBot=_n_commands_admin_kick_missingPermissionBot,
        noReasonProvided=LocalizedString('commands.admin.kick.noReasonProvided'),
        success=_n_commands_admin_kick_success,
        targetTooHigh=_n_commands_admin_kick_targetTooHigh,
    )
    _n_commands_admin_lock_alreadyLocked = CommandsAdminLockAlreadyLocked(
        description=LocalizedString('commands.admin.lock.alreadyLocked.description'),
        title=LocalizedString('commands.admin.lock.alreadyLocked.title'),
    )
    _n_commands_admin_lock_error = CommandsAdminLockError(
        description=LocalizedString('commands.admin.lock.error.description'),
        title=LocalizedString('commands.admin.lock.error.title'),
    )
    _n_commands_admin_lock_forbidden = CommandsAdminLockForbidden(
        description=LocalizedString('commands.admin.lock.forbidden.description'),
        title=LocalizedString('commands.admin.lock.forbidden.title'),
    )
    _n_commands_admin_lock_missingPermission = CommandsAdminLockMissingPermission(
        description=LocalizedString('commands.admin.lock.missingPermission.description'),
        title=LocalizedString('commands.admin.lock.missingPermission.title'),
    )
    _n_commands_admin_lock_missingPermissionBot = CommandsAdminLockMissingPermissionBot(
        description=LocalizedString('commands.admin.lock.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.lock.missingPermissionBot.title'),
    )
    _n_commands_admin_lock_success = CommandsAdminLockSuccess(
        description=LocalizedString('commands.admin.lock.success.description'),
        title=LocalizedString('commands.admin.lock.success.title'),
    )
    _n_commands_admin_lock = CommandsAdminLock(
        alreadyLocked=_n_commands_admin_lock_alreadyLocked,
        channelLockedMessage=LocalizedString('commands.admin.lock.channelLockedMessage'),
        error=_n_commands_admin_lock_error,
        forbidden=_n_commands_admin_lock_forbidden,
        missingPermission=_n_commands_admin_lock_missingPermission,
        missingPermissionBot=_n_commands_admin_lock_missingPermissionBot,
        success=_n_commands_admin_lock_success,
    )
    _n_commands_admin_moverole_error = CommandsAdminMoveroleError(
        description=LocalizedString('commands.admin.moverole.error.description'),
        title=LocalizedString('commands.admin.moverole.error.title'),
    )
    _n_commands_admin_moverole_forbidden = CommandsAdminMoveroleForbidden(
        description=LocalizedString('commands.admin.moverole.forbidden.description'),
        title=LocalizedString('commands.admin.moverole.forbidden.title'),
    )
    _n_commands_admin_moverole_missingPermission = CommandsAdminMoveroleMissingPermission(
        description=LocalizedString('commands.admin.moverole.missingPermission.description'),
        title=LocalizedString('commands.admin.moverole.missingPermission.title'),
    )
    _n_commands_admin_moverole_missingPermissionBot = CommandsAdminMoveroleMissingPermissionBot(
        description=LocalizedString('commands.admin.moverole.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.moverole.missingPermissionBot.title'),
    )
    _n_commands_admin_moverole_roleTooHigh = CommandsAdminMoveroleRoleTooHigh(
        description=LocalizedString('commands.admin.moverole.roleTooHigh.description'),
        title=LocalizedString('commands.admin.moverole.roleTooHigh.title'),
    )
    _n_commands_admin_moverole_success = CommandsAdminMoveroleSuccess(
        description=LocalizedString('commands.admin.moverole.success.description'),
        title=LocalizedString('commands.admin.moverole.success.title'),
    )
    _n_commands_admin_moverole = CommandsAdminMoverole(
        error=_n_commands_admin_moverole_error,
        forbidden=_n_commands_admin_moverole_forbidden,
        missingPermission=_n_commands_admin_moverole_missingPermission,
        missingPermissionBot=_n_commands_admin_moverole_missingPermissionBot,
        roleTooHigh=_n_commands_admin_moverole_roleTooHigh,
        success=_n_commands_admin_moverole_success,
    )
    _n_commands_admin_nickname_changed = CommandsAdminNicknameChanged(
        description=LocalizedString('commands.admin.nickname.changed.description'),
        title=LocalizedString('commands.admin.nickname.changed.title'),
    )
    _n_commands_admin_nickname_error = CommandsAdminNicknameError(
        description=LocalizedString('commands.admin.nickname.error.description'),
        title=LocalizedString('commands.admin.nickname.error.title'),
    )
    _n_commands_admin_nickname_forbidden = CommandsAdminNicknameForbidden(
        description=LocalizedString('commands.admin.nickname.forbidden.description'),
        title=LocalizedString('commands.admin.nickname.forbidden.title'),
    )
    _n_commands_admin_nickname_missingPermission = CommandsAdminNicknameMissingPermission(
        description=LocalizedString('commands.admin.nickname.missingPermission.description'),
        title=LocalizedString('commands.admin.nickname.missingPermission.title'),
    )
    _n_commands_admin_nickname_missingPermissionBot = CommandsAdminNicknameMissingPermissionBot(
        description=LocalizedString('commands.admin.nickname.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.nickname.missingPermissionBot.title'),
    )
    _n_commands_admin_nickname_removed = CommandsAdminNicknameRemoved(
        description=LocalizedString('commands.admin.nickname.removed.description'),
        title=LocalizedString('commands.admin.nickname.removed.title'),
    )
    _n_commands_admin_nickname_targetTooHigh = CommandsAdminNicknameTargetTooHigh(
        description=LocalizedString('commands.admin.nickname.targetTooHigh.description'),
        title=LocalizedString('commands.admin.nickname.targetTooHigh.title'),
    )
    _n_commands_admin_nickname = CommandsAdminNickname(
        changed=_n_commands_admin_nickname_changed,
        error=_n_commands_admin_nickname_error,
        forbidden=_n_commands_admin_nickname_forbidden,
        missingPermission=_n_commands_admin_nickname_missingPermission,
        missingPermissionBot=_n_commands_admin_nickname_missingPermissionBot,
        removed=_n_commands_admin_nickname_removed,
        targetTooHigh=_n_commands_admin_nickname_targetTooHigh,
    )
    _n_commands_admin_nuke_missingPermission = CommandsAdminNukeMissingPermission(
        description=LocalizedString('commands.admin.nuke.missingPermission.description'),
        title=LocalizedString('commands.admin.nuke.missingPermission.title'),
    )
    _n_commands_admin_nuke_missingPermissionBot = CommandsAdminNukeMissingPermissionBot(
        description=LocalizedString('commands.admin.nuke.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.nuke.missingPermissionBot.title'),
    )
    _n_commands_admin_nuke_notfound = CommandsAdminNukeNotfound(
        description=LocalizedString('commands.admin.nuke.notfound.description'),
        title=LocalizedString('commands.admin.nuke.notfound.title'),
    )
    _n_commands_admin_nuke = CommandsAdminNuke(
        cancel=LocalizedString('commands.admin.nuke.cancel'),
        cancelledMessage=LocalizedString('commands.admin.nuke.cancelledMessage'),
        confirm=LocalizedString('commands.admin.nuke.confirm'),
        confirmationDescription=LocalizedString('commands.admin.nuke.confirmationDescription'),
        confirmationPrompt=LocalizedString('commands.admin.nuke.confirmationPrompt'),
        confirmationTitle=LocalizedString('commands.admin.nuke.confirmationTitle'),
        confirmationWord=LocalizedString('commands.admin.nuke.confirmationWord'),
        forbiddenError=LocalizedString('commands.admin.nuke.forbiddenError'),
        httpError=LocalizedString('commands.admin.nuke.httpError'),
        incorrectConfirmation=LocalizedString('commands.admin.nuke.incorrectConfirmation'),
        missingPermission=_n_commands_admin_nuke_missingPermission,
        missingPermissionBot=_n_commands_admin_nuke_missingPermissionBot,
        notfound=_n_commands_admin_nuke_notfound,
        nukeReason=LocalizedString('commands.admin.nuke.nukeReason'),
        nukeSuccessMessage=LocalizedString('commands.admin.nuke.nukeSuccessMessage'),
        timeoutMessage=LocalizedString('commands.admin.nuke.timeoutMessage'),
        unauthorizedUser=LocalizedString('commands.admin.nuke.unauthorizedUser'),
    )
    _n_commands_admin_open_ticket_error_success = CommandsAdminOpen_ticketErrorSuccess(
        ticketCreated=LocalizedString('commands.admin.open_ticket.error.success.ticketCreated'),
    )
    _n_commands_admin_open_ticket_error = CommandsAdminOpen_ticketError(
        channelMissingPermission=LocalizedString('commands.admin.open_ticket.error.channelMissingPermission'),
        success=_n_commands_admin_open_ticket_error_success,
        ticketCreated=LocalizedString('commands.admin.open_ticket.error.ticketCreated'),
        ticketNotCreated=LocalizedString('commands.admin.open_ticket.error.ticketNotCreated'),
        ticketNotFound=LocalizedString('commands.admin.open_ticket.error.ticketNotFound'),
    )
    _n_commands_admin_open_ticket_optedOutWarning = CommandsAdminOpen_ticketOptedOutWarning(
        confirm=LocalizedString('commands.admin.open_ticket.optedOutWarning.confirm'),
        decline=LocalizedString('commands.admin.open_ticket.optedOutWarning.decline'),
        declined=LocalizedString('commands.admin.open_ticket.optedOutWarning.declined'),
        description=LocalizedString('commands.admin.open_ticket.optedOutWarning.description'),
    )
    _n_commands_admin_open_ticket_success = CommandsAdminOpen_ticketSuccess(
        ticketCreated=LocalizedString('commands.admin.open_ticket.success.ticketCreated'),
    )
    _n_commands_admin_open_ticket = CommandsAdminOpen_ticket(
        error=_n_commands_admin_open_ticket_error,
        optedOutWarning=_n_commands_admin_open_ticket_optedOutWarning,
        success=_n_commands_admin_open_ticket_success,
    )
    _n_commands_admin_purge_error = CommandsAdminPurgeError(
        description=LocalizedString('commands.admin.purge.error.description'),
        title=LocalizedString('commands.admin.purge.error.title'),
    )
    _n_commands_admin_purge_forbidden = CommandsAdminPurgeForbidden(
        description=LocalizedString('commands.admin.purge.forbidden.description'),
        title=LocalizedString('commands.admin.purge.forbidden.title'),
    )
    _n_commands_admin_purge_invalidAmount = CommandsAdminPurgeInvalidAmount(
        description=LocalizedString('commands.admin.purge.invalidAmount.description'),
        title=LocalizedString('commands.admin.purge.invalidAmount.title'),
    )
    _n_commands_admin_purge_missingPermission = CommandsAdminPurgeMissingPermission(
        description=LocalizedString('commands.admin.purge.missingPermission.description'),
        title=LocalizedString('commands.admin.purge.missingPermission.title'),
    )
    _n_commands_admin_purge_missingPermissionBot = CommandsAdminPurgeMissingPermissionBot(
        description=LocalizedString('commands.admin.purge.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.purge.missingPermissionBot.title'),
    )
    _n_commands_admin_purge_success = CommandsAdminPurgeSuccess(
        description=LocalizedString('commands.admin.purge.success.description'),
        title=LocalizedString('commands.admin.purge.success.title'),
    )
    _n_commands_admin_purge = CommandsAdminPurge(
        error=_n_commands_admin_purge_error,
        forbidden=_n_commands_admin_purge_forbidden,
        invalidAmount=_n_commands_admin_purge_invalidAmount,
        missingPermission=_n_commands_admin_purge_missingPermission,
        missingPermissionBot=_n_commands_admin_purge_missingPermissionBot,
        success=_n_commands_admin_purge_success,
    )
    _n_commands_admin_remove_role_multipleSuccess = CommandsAdminRemove_roleMultipleSuccess(
        action=LocalizedString('commands.admin.remove_role.multipleSuccess.action'),
    )
    _n_commands_admin_remove_role = CommandsAdminRemove_role(
        multipleSuccess=_n_commands_admin_remove_role_multipleSuccess,
    )
    _n_commands_admin_remove_timeout_error = CommandsAdminRemove_timeoutError(
        description=LocalizedString('commands.admin.remove_timeout.error.description'),
        title=LocalizedString('commands.admin.remove_timeout.error.title'),
    )
    _n_commands_admin_remove_timeout_forbidden = CommandsAdminRemove_timeoutForbidden(
        description=LocalizedString('commands.admin.remove_timeout.forbidden.description'),
        title=LocalizedString('commands.admin.remove_timeout.forbidden.title'),
    )
    _n_commands_admin_remove_timeout_missingPermission = CommandsAdminRemove_timeoutMissingPermission(
        description=LocalizedString('commands.admin.remove_timeout.missingPermission.description'),
        title=LocalizedString('commands.admin.remove_timeout.missingPermission.title'),
    )
    _n_commands_admin_remove_timeout_missingPermissionBot = CommandsAdminRemove_timeoutMissingPermissionBot(
        description=LocalizedString('commands.admin.remove_timeout.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.remove_timeout.missingPermissionBot.title'),
    )
    _n_commands_admin_remove_timeout_notTimedOut = CommandsAdminRemove_timeoutNotTimedOut(
        description=LocalizedString('commands.admin.remove_timeout.notTimedOut.description'),
        title=LocalizedString('commands.admin.remove_timeout.notTimedOut.title'),
    )
    _n_commands_admin_remove_timeout_success = CommandsAdminRemove_timeoutSuccess(
        description=LocalizedString('commands.admin.remove_timeout.success.description'),
        title=LocalizedString('commands.admin.remove_timeout.success.title'),
    )
    _n_commands_admin_remove_timeout_targetTooHigh = CommandsAdminRemove_timeoutTargetTooHigh(
        description=LocalizedString('commands.admin.remove_timeout.targetTooHigh.description'),
        title=LocalizedString('commands.admin.remove_timeout.targetTooHigh.title'),
    )
    _n_commands_admin_remove_timeout = CommandsAdminRemove_timeout(
        error=_n_commands_admin_remove_timeout_error,
        forbidden=_n_commands_admin_remove_timeout_forbidden,
        missingPermission=_n_commands_admin_remove_timeout_missingPermission,
        missingPermissionBot=_n_commands_admin_remove_timeout_missingPermissionBot,
        noReasonProvided=LocalizedString('commands.admin.remove_timeout.noReasonProvided'),
        notTimedOut=_n_commands_admin_remove_timeout_notTimedOut,
        success=_n_commands_admin_remove_timeout_success,
        targetTooHigh=_n_commands_admin_remove_timeout_targetTooHigh,
    )
    _n_commands_admin_removejointocreatechannel_alreadySet = CommandsAdminRemovejointocreatechannelAlreadySet(
        description=LocalizedString('commands.admin.removejointocreatechannel.alreadySet.description'),
        title=LocalizedString('commands.admin.removejointocreatechannel.alreadySet.title'),
    )
    _n_commands_admin_removejointocreatechannel_missingPermission = CommandsAdminRemovejointocreatechannelMissingPermission(
        description=LocalizedString('commands.admin.removejointocreatechannel.missingPermission.description'),
        title=LocalizedString('commands.admin.removejointocreatechannel.missingPermission.title'),
    )
    _n_commands_admin_removejointocreatechannel_notSet = CommandsAdminRemovejointocreatechannelNotSet(
        description=LocalizedString('commands.admin.removejointocreatechannel.notSet.description'),
        title=LocalizedString('commands.admin.removejointocreatechannel.notSet.title'),
    )
    _n_commands_admin_removejointocreatechannel_success = CommandsAdminRemovejointocreatechannelSuccess(
        description=LocalizedString('commands.admin.removejointocreatechannel.success.description'),
        title=LocalizedString('commands.admin.removejointocreatechannel.success.title'),
    )
    _n_commands_admin_removejointocreatechannel = CommandsAdminRemovejointocreatechannel(
        alreadySet=_n_commands_admin_removejointocreatechannel_alreadySet,
        missingPermission=_n_commands_admin_removejointocreatechannel_missingPermission,
        notSet=_n_commands_admin_removejointocreatechannel_notSet,
        success=_n_commands_admin_removejointocreatechannel_success,
    )
    _n_commands_admin_removerole_cancel = CommandsAdminRemoveroleCancel(
        _text=LocalizedString('commands.admin.removerole.cancel'),
        label=LocalizedString('commands.admin.removerole.cancel.label'),
    )
    _n_commands_admin_removerole_confirm = CommandsAdminRemoveroleConfirm(
        _text=LocalizedString('commands.admin.removerole.confirm'),
        label=LocalizedString('commands.admin.removerole.confirm.label'),
    )
    _n_commands_admin_removerole_doesNotHaveRole = CommandsAdminRemoveroleDoesNotHaveRole(
        description=LocalizedString('commands.admin.removerole.doesNotHaveRole.description'),
        title=LocalizedString('commands.admin.removerole.doesNotHaveRole.title'),
    )
    _n_commands_admin_removerole_managedRole = CommandsAdminRemoveroleManagedRole(
        description=LocalizedString('commands.admin.removerole.managedRole.description'),
        title=LocalizedString('commands.admin.removerole.managedRole.title'),
    )
    _n_commands_admin_removerole_missingPermission = CommandsAdminRemoveroleMissingPermission(
        description=LocalizedString('commands.admin.removerole.missingPermission.description'),
        title=LocalizedString('commands.admin.removerole.missingPermission.title'),
    )
    _n_commands_admin_removerole_missingPermissionBot = CommandsAdminRemoveroleMissingPermissionBot(
        description=LocalizedString('commands.admin.removerole.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.removerole.missingPermissionBot.title'),
    )
    _n_commands_admin_removerole_noRole = CommandsAdminRemoveroleNoRole(
        description=LocalizedString('commands.admin.removerole.noRole.description'),
        title=LocalizedString('commands.admin.removerole.noRole.title'),
    )
    _n_commands_admin_removerole_noUser = CommandsAdminRemoveroleNoUser(
        description=LocalizedString('commands.admin.removerole.noUser.description'),
        title=LocalizedString('commands.admin.removerole.noUser.title'),
    )
    _n_commands_admin_removerole_roleTooHigh = CommandsAdminRemoveroleRoleTooHigh(
        description=LocalizedString('commands.admin.removerole.roleTooHigh.description'),
        title=LocalizedString('commands.admin.removerole.roleTooHigh.title'),
    )
    _n_commands_admin_removerole_roleTooHighBot = CommandsAdminRemoveroleRoleTooHighBot(
        description=LocalizedString('commands.admin.removerole.roleTooHighBot.description'),
        title=LocalizedString('commands.admin.removerole.roleTooHighBot.title'),
    )
    _n_commands_admin_removerole_success = CommandsAdminRemoveroleSuccess(
        description=LocalizedString('commands.admin.removerole.success.description'),
        title=LocalizedString('commands.admin.removerole.success.title'),
    )
    _n_commands_admin_removerole = CommandsAdminRemoverole(
        cancel=_n_commands_admin_removerole_cancel,
        cancelled=LocalizedString('commands.admin.removerole.cancelled'),
        confirm=_n_commands_admin_removerole_confirm,
        doesNotHaveRole=_n_commands_admin_removerole_doesNotHaveRole,
        error=LocalizedString('commands.admin.removerole.error'),
        managedRole=_n_commands_admin_removerole_managedRole,
        missingPermission=_n_commands_admin_removerole_missingPermission,
        missingPermissionBot=_n_commands_admin_removerole_missingPermissionBot,
        multiplePrompt=LocalizedString('commands.admin.removerole.multiplePrompt'),
        multipleSuccess=LocalizedString('commands.admin.removerole.multipleSuccess'),
        noRole=_n_commands_admin_removerole_noRole,
        noSelection=LocalizedString('commands.admin.removerole.noSelection'),
        noUser=_n_commands_admin_removerole_noUser,
        roleTooHigh=_n_commands_admin_removerole_roleTooHigh,
        roleTooHighBot=_n_commands_admin_removerole_roleTooHighBot,
        selectRoles=LocalizedString('commands.admin.removerole.selectRoles'),
        selectUsers=LocalizedString('commands.admin.removerole.selectUsers'),
        success=_n_commands_admin_removerole_success,
    )
    _n_commands_admin_reports_remove_channel_missingPermission = CommandsAdminReportsRemove_channelMissingPermission(
        description=LocalizedString('commands.admin.reports.remove_channel.missingPermission.description'),
        title=LocalizedString('commands.admin.reports.remove_channel.missingPermission.title'),
    )
    _n_commands_admin_reports_remove_channel_noChannel = CommandsAdminReportsRemove_channelNoChannel(
        description=LocalizedString('commands.admin.reports.remove_channel.noChannel.description'),
        title=LocalizedString('commands.admin.reports.remove_channel.noChannel.title'),
    )
    _n_commands_admin_reports_remove_channel_success = CommandsAdminReportsRemove_channelSuccess(
        description=LocalizedString('commands.admin.reports.remove_channel.success.description'),
        title=LocalizedString('commands.admin.reports.remove_channel.success.title'),
    )
    _n_commands_admin_reports_remove_channel = CommandsAdminReportsRemove_channel(
        missingPermission=_n_commands_admin_reports_remove_channel_missingPermission,
        noChannel=_n_commands_admin_reports_remove_channel_noChannel,
        success=_n_commands_admin_reports_remove_channel_success,
    )
    _n_commands_admin_reports_set_channel_alreadySet = CommandsAdminReportsSet_channelAlreadySet(
        description=LocalizedString('commands.admin.reports.set_channel.alreadySet.description'),
        title=LocalizedString('commands.admin.reports.set_channel.alreadySet.title'),
    )
    _n_commands_admin_reports_set_channel_missingPermission = CommandsAdminReportsSet_channelMissingPermission(
        description=LocalizedString('commands.admin.reports.set_channel.missingPermission.description'),
        title=LocalizedString('commands.admin.reports.set_channel.missingPermission.title'),
    )
    _n_commands_admin_reports_set_channel_missingPermissionBot = CommandsAdminReportsSet_channelMissingPermissionBot(
        description=LocalizedString('commands.admin.reports.set_channel.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.reports.set_channel.missingPermissionBot.title'),
    )
    _n_commands_admin_reports_set_channel_success = CommandsAdminReportsSet_channelSuccess(
        description=LocalizedString('commands.admin.reports.set_channel.success.description'),
        title=LocalizedString('commands.admin.reports.set_channel.success.title'),
    )
    _n_commands_admin_reports_set_channel = CommandsAdminReportsSet_channel(
        alreadySet=_n_commands_admin_reports_set_channel_alreadySet,
        missingPermission=_n_commands_admin_reports_set_channel_missingPermission,
        missingPermissionBot=_n_commands_admin_reports_set_channel_missingPermissionBot,
        success=_n_commands_admin_reports_set_channel_success,
    )
    _n_commands_admin_reports_show_reports_block = CommandsAdminReportsShow_reportsBlock(
        label=LocalizedString('commands.admin.reports.show_reports.block.label'),
    )
    _n_commands_admin_reports_show_reports_missingPermission = CommandsAdminReportsShow_reportsMissingPermission(
        description=LocalizedString('commands.admin.reports.show_reports.missingPermission.description'),
        title=LocalizedString('commands.admin.reports.show_reports.missingPermission.title'),
    )
    _n_commands_admin_reports_show_reports_next = CommandsAdminReportsShow_reportsNext(
        label=LocalizedString('commands.admin.reports.show_reports.next.label'),
    )
    _n_commands_admin_reports_show_reports_noReports = CommandsAdminReportsShow_reportsNoReports(
        description=LocalizedString('commands.admin.reports.show_reports.noReports.description'),
        title=LocalizedString('commands.admin.reports.show_reports.noReports.title'),
    )
    _n_commands_admin_reports_show_reports_previous = CommandsAdminReportsShow_reportsPrevious(
        label=LocalizedString('commands.admin.reports.show_reports.previous.label'),
    )
    _n_commands_admin_reports_show_reports_remove = CommandsAdminReportsShow_reportsRemove(
        label=LocalizedString('commands.admin.reports.show_reports.remove.label'),
    )
    _n_commands_admin_reports_show_reports_report = CommandsAdminReportsShow_reportsReport(
        accepted=LocalizedString('commands.admin.reports.show_reports.report.accepted'),
        description=LocalizedString('commands.admin.reports.show_reports.report.description'),
        not_accepted=LocalizedString('commands.admin.reports.show_reports.report.not_accepted'),
        not_resolved=LocalizedString('commands.admin.reports.show_reports.report.not_resolved'),
        resolved=LocalizedString('commands.admin.reports.show_reports.report.resolved'),
        status=LocalizedString('commands.admin.reports.show_reports.report.status'),
        title=LocalizedString('commands.admin.reports.show_reports.report.title'),
    )
    _n_commands_admin_reports_show_reports_resolve = CommandsAdminReportsShow_reportsResolve(
        label=LocalizedString('commands.admin.reports.show_reports.resolve.label'),
    )
    _n_commands_admin_reports_show_reports_unblock = CommandsAdminReportsShow_reportsUnblock(
        label=LocalizedString('commands.admin.reports.show_reports.unblock.label'),
    )
    _n_commands_admin_reports_show_reports = CommandsAdminReportsShow_reports(
        block=_n_commands_admin_reports_show_reports_block,
        missingPermission=_n_commands_admin_reports_show_reports_missingPermission,
        next=_n_commands_admin_reports_show_reports_next,
        noReports=_n_commands_admin_reports_show_reports_noReports,
        not_your_reports=LocalizedString('commands.admin.reports.show_reports.not_your_reports'),
        not_your_warns=LocalizedString('commands.admin.reports.show_reports.not_your_warns'),
        previous=_n_commands_admin_reports_show_reports_previous,
        remove=_n_commands_admin_reports_show_reports_remove,
        report=_n_commands_admin_reports_show_reports_report,
        resolve=_n_commands_admin_reports_show_reports_resolve,
        unblock=_n_commands_admin_reports_show_reports_unblock,
    )
    _n_commands_admin_reports_unblock_reporter_missingPermission = CommandsAdminReportsUnblock_reporterMissingPermission(
        description=LocalizedString('commands.admin.reports.unblock_reporter.missingPermission.description'),
        title=LocalizedString('commands.admin.reports.unblock_reporter.missingPermission.title'),
    )
    _n_commands_admin_reports_unblock_reporter_notBlocked = CommandsAdminReportsUnblock_reporterNotBlocked(
        description=LocalizedString('commands.admin.reports.unblock_reporter.notBlocked.description'),
        title=LocalizedString('commands.admin.reports.unblock_reporter.notBlocked.title'),
    )
    _n_commands_admin_reports_unblock_reporter_success = CommandsAdminReportsUnblock_reporterSuccess(
        description=LocalizedString('commands.admin.reports.unblock_reporter.success.description'),
        title=LocalizedString('commands.admin.reports.unblock_reporter.success.title'),
    )
    _n_commands_admin_reports_unblock_reporter = CommandsAdminReportsUnblock_reporter(
        missingPermission=_n_commands_admin_reports_unblock_reporter_missingPermission,
        notBlocked=_n_commands_admin_reports_unblock_reporter_notBlocked,
        success=_n_commands_admin_reports_unblock_reporter_success,
    )
    _n_commands_admin_reports = CommandsAdminReports(
        remove_channel=_n_commands_admin_reports_remove_channel,
        set_channel=_n_commands_admin_reports_set_channel,
        show_reports=_n_commands_admin_reports_show_reports,
        unblock_reporter=_n_commands_admin_reports_unblock_reporter,
    )
    _n_commands_admin_say_error = CommandsAdminSayError(
        description=LocalizedString('commands.admin.say.error.description'),
        title=LocalizedString('commands.admin.say.error.title'),
    )
    _n_commands_admin_say_missingPermission = CommandsAdminSayMissingPermission(
        description=LocalizedString('commands.admin.say.missingPermission.description'),
        title=LocalizedString('commands.admin.say.missingPermission.title'),
    )
    _n_commands_admin_say_missingPermissionBot = CommandsAdminSayMissingPermissionBot(
        description=LocalizedString('commands.admin.say.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.say.missingPermissionBot.title'),
    )
    _n_commands_admin_say_success = CommandsAdminSaySuccess(
        description=LocalizedString('commands.admin.say.success.description'),
        title=LocalizedString('commands.admin.say.success.title'),
    )
    _n_commands_admin_say = CommandsAdminSay(
        error=_n_commands_admin_say_error,
        missingPermission=_n_commands_admin_say_missingPermission,
        missingPermissionBot=_n_commands_admin_say_missingPermissionBot,
        success=_n_commands_admin_say_success,
    )
    _n_commands_admin_setLocale_missingPermission = CommandsAdminSetLocaleMissingPermission(
        description=LocalizedString('commands.admin.setLocale.missingPermission.description'),
        title=LocalizedString('commands.admin.setLocale.missingPermission.title'),
    )
    _n_commands_admin_setLocale_success = CommandsAdminSetLocaleSuccess(
        description=LocalizedString('commands.admin.setLocale.success.description'),
        title=LocalizedString('commands.admin.setLocale.success.title'),
    )
    _n_commands_admin_setLocale = CommandsAdminSetLocale(
        missingPermission=_n_commands_admin_setLocale_missingPermission,
        setLocaleReason=LocalizedString('commands.admin.setLocale.setLocaleReason'),
        success=_n_commands_admin_setLocale_success,
    )
    _n_commands_admin_slowmode_disabled = CommandsAdminSlowmodeDisabled(
        description=LocalizedString('commands.admin.slowmode.disabled.description'),
        title=LocalizedString('commands.admin.slowmode.disabled.title'),
    )
    _n_commands_admin_slowmode_enabled = CommandsAdminSlowmodeEnabled(
        description=LocalizedString('commands.admin.slowmode.enabled.description'),
        title=LocalizedString('commands.admin.slowmode.enabled.title'),
    )
    _n_commands_admin_slowmode_error = CommandsAdminSlowmodeError(
        description=LocalizedString('commands.admin.slowmode.error.description'),
        title=LocalizedString('commands.admin.slowmode.error.title'),
    )
    _n_commands_admin_slowmode_forbidden = CommandsAdminSlowmodeForbidden(
        description=LocalizedString('commands.admin.slowmode.forbidden.description'),
        title=LocalizedString('commands.admin.slowmode.forbidden.title'),
    )
    _n_commands_admin_slowmode_invalidDuration = CommandsAdminSlowmodeInvalidDuration(
        description=LocalizedString('commands.admin.slowmode.invalidDuration.description'),
        title=LocalizedString('commands.admin.slowmode.invalidDuration.title'),
    )
    _n_commands_admin_slowmode_missingPermission = CommandsAdminSlowmodeMissingPermission(
        description=LocalizedString('commands.admin.slowmode.missingPermission.description'),
        title=LocalizedString('commands.admin.slowmode.missingPermission.title'),
    )
    _n_commands_admin_slowmode_missingPermissionBot = CommandsAdminSlowmodeMissingPermissionBot(
        description=LocalizedString('commands.admin.slowmode.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.slowmode.missingPermissionBot.title'),
    )
    _n_commands_admin_slowmode = CommandsAdminSlowmode(
        disabled=_n_commands_admin_slowmode_disabled,
        enabled=_n_commands_admin_slowmode_enabled,
        error=_n_commands_admin_slowmode_error,
        forbidden=_n_commands_admin_slowmode_forbidden,
        invalidDuration=_n_commands_admin_slowmode_invalidDuration,
        missingPermission=_n_commands_admin_slowmode_missingPermission,
        missingPermissionBot=_n_commands_admin_slowmode_missingPermissionBot,
    )
    _n_commands_admin_sync = CommandsAdminSync(
        completed=LocalizedString('commands.admin.sync.completed'),
        failed=LocalizedString('commands.admin.sync.failed'),
        in_progress=LocalizedString('commands.admin.sync.in_progress'),
    )
    _n_commands_admin_timeout_alreadyTimedOut = CommandsAdminTimeoutAlreadyTimedOut(
        description=LocalizedString('commands.admin.timeout.alreadyTimedOut.description'),
        title=LocalizedString('commands.admin.timeout.alreadyTimedOut.title'),
    )
    _n_commands_admin_timeout_error = CommandsAdminTimeoutError(
        description=LocalizedString('commands.admin.timeout.error.description'),
        title=LocalizedString('commands.admin.timeout.error.title'),
    )
    _n_commands_admin_timeout_forbidden = CommandsAdminTimeoutForbidden(
        description=LocalizedString('commands.admin.timeout.forbidden.description'),
        title=LocalizedString('commands.admin.timeout.forbidden.title'),
    )
    _n_commands_admin_timeout_invalidDuration = CommandsAdminTimeoutInvalidDuration(
        description=LocalizedString('commands.admin.timeout.invalidDuration.description'),
        title=LocalizedString('commands.admin.timeout.invalidDuration.title'),
    )
    _n_commands_admin_timeout_missingPermission = CommandsAdminTimeoutMissingPermission(
        description=LocalizedString('commands.admin.timeout.missingPermission.description'),
        title=LocalizedString('commands.admin.timeout.missingPermission.title'),
    )
    _n_commands_admin_timeout_missingPermissionBot = CommandsAdminTimeoutMissingPermissionBot(
        description=LocalizedString('commands.admin.timeout.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.timeout.missingPermissionBot.title'),
    )
    _n_commands_admin_timeout_success = CommandsAdminTimeoutSuccess(
        description=LocalizedString('commands.admin.timeout.success.description'),
        title=LocalizedString('commands.admin.timeout.success.title'),
    )
    _n_commands_admin_timeout_targetTooHigh = CommandsAdminTimeoutTargetTooHigh(
        description=LocalizedString('commands.admin.timeout.targetTooHigh.description'),
        title=LocalizedString('commands.admin.timeout.targetTooHigh.title'),
    )
    _n_commands_admin_timeout = CommandsAdminTimeout(
        alreadyTimedOut=_n_commands_admin_timeout_alreadyTimedOut,
        error=_n_commands_admin_timeout_error,
        forbidden=_n_commands_admin_timeout_forbidden,
        invalidDuration=_n_commands_admin_timeout_invalidDuration,
        missingPermission=_n_commands_admin_timeout_missingPermission,
        missingPermissionBot=_n_commands_admin_timeout_missingPermissionBot,
        noReasonProvided=LocalizedString('commands.admin.timeout.noReasonProvided'),
        success=_n_commands_admin_timeout_success,
        targetTooHigh=_n_commands_admin_timeout_targetTooHigh,
    )
    _n_commands_admin_trigger_messages_add_missingPermission = CommandsAdminTrigger_messagesAddMissingPermission(
        description=LocalizedString('commands.admin.trigger_messages.add.missingPermission.description'),
        title=LocalizedString('commands.admin.trigger_messages.add.missingPermission.title'),
    )
    _n_commands_admin_trigger_messages_add_success = CommandsAdminTrigger_messagesAddSuccess(
        description=LocalizedString('commands.admin.trigger_messages.add.success.description'),
        title=LocalizedString('commands.admin.trigger_messages.add.success.title'),
    )
    _n_commands_admin_trigger_messages_add = CommandsAdminTrigger_messagesAdd(
        missingPermission=_n_commands_admin_trigger_messages_add_missingPermission,
        success=_n_commands_admin_trigger_messages_add_success,
    )
    _n_commands_admin_trigger_messages_configure_add_channel = CommandsAdminTrigger_messagesConfigureAdd_channel(
        label=LocalizedString('commands.admin.trigger_messages.configure.add_channel.label'),
    )
    _n_commands_admin_trigger_messages_configure_down = CommandsAdminTrigger_messagesConfigureDown(
        label=LocalizedString('commands.admin.trigger_messages.configure.down.label'),
    )
    _n_commands_admin_trigger_messages_configure_missingPermission = CommandsAdminTrigger_messagesConfigureMissingPermission(
        description=LocalizedString('commands.admin.trigger_messages.configure.missingPermission.description'),
        title=LocalizedString('commands.admin.trigger_messages.configure.missingPermission.title'),
    )
    _n_commands_admin_trigger_messages_configure_modal_caseSensitive = CommandsAdminTrigger_messagesConfigureModalCaseSensitive(
        label=LocalizedString('commands.admin.trigger_messages.configure.modal.caseSensitive.label'),
        placeholder=LocalizedString('commands.admin.trigger_messages.configure.modal.caseSensitive.placeholder'),
    )
    _n_commands_admin_trigger_messages_configure_modal_case_sensitive = CommandsAdminTrigger_messagesConfigureModalCase_sensitive(
        label=LocalizedString('commands.admin.trigger_messages.configure.modal.case_sensitive.label'),
        placeholder=LocalizedString('commands.admin.trigger_messages.configure.modal.case_sensitive.placeholder'),
    )
    _n_commands_admin_trigger_messages_configure_modal_response = CommandsAdminTrigger_messagesConfigureModalResponse(
        label=LocalizedString('commands.admin.trigger_messages.configure.modal.response.label'),
        placeholder=LocalizedString('commands.admin.trigger_messages.configure.modal.response.placeholder'),
    )
    _n_commands_admin_trigger_messages_configure_modal_trigger = CommandsAdminTrigger_messagesConfigureModalTrigger(
        label=LocalizedString('commands.admin.trigger_messages.configure.modal.trigger.label'),
        placeholder=LocalizedString('commands.admin.trigger_messages.configure.modal.trigger.placeholder'),
    )
    _n_commands_admin_trigger_messages_configure_modal = CommandsAdminTrigger_messagesConfigureModal(
        caseSensitive=_n_commands_admin_trigger_messages_configure_modal_caseSensitive,
        case_sensitive=_n_commands_admin_trigger_messages_configure_modal_case_sensitive,
        response=_n_commands_admin_trigger_messages_configure_modal_response,
        title=LocalizedString('commands.admin.trigger_messages.configure.modal.title'),
        trigger=_n_commands_admin_trigger_messages_configure_modal_trigger,
    )
    _n_commands_admin_trigger_messages_configure_new = CommandsAdminTrigger_messagesConfigureNew(
        label=LocalizedString('commands.admin.trigger_messages.configure.new.label'),
    )
    _n_commands_admin_trigger_messages_configure_next = CommandsAdminTrigger_messagesConfigureNext(
        label=LocalizedString('commands.admin.trigger_messages.configure.next.label'),
    )
    _n_commands_admin_trigger_messages_configure_noTriggerMessages = CommandsAdminTrigger_messagesConfigureNoTriggerMessages(
        description=LocalizedString('commands.admin.trigger_messages.configure.noTriggerMessages.description'),
        title=LocalizedString('commands.admin.trigger_messages.configure.noTriggerMessages.title'),
    )
    _n_commands_admin_trigger_messages_configure_previous = CommandsAdminTrigger_messagesConfigurePrevious(
        label=LocalizedString('commands.admin.trigger_messages.configure.previous.label'),
    )
    _n_commands_admin_trigger_messages_configure_remove = CommandsAdminTrigger_messagesConfigureRemove(
        label=LocalizedString('commands.admin.trigger_messages.configure.remove.label'),
    )
    _n_commands_admin_trigger_messages_configure_remove_channel = CommandsAdminTrigger_messagesConfigureRemove_channel(
        label=LocalizedString('commands.admin.trigger_messages.configure.remove_channel.label'),
    )
    _n_commands_admin_trigger_messages_configure_trigger_addChannel = CommandsAdminTrigger_messagesConfigureTriggerAddChannel(
        description=LocalizedString('commands.admin.trigger_messages.configure.trigger.addChannel.description'),
        placeholder=LocalizedString('commands.admin.trigger_messages.configure.trigger.addChannel.placeholder'),
        title=LocalizedString('commands.admin.trigger_messages.configure.trigger.addChannel.title'),
    )
    _n_commands_admin_trigger_messages_configure_trigger_noTriggerMessages = CommandsAdminTrigger_messagesConfigureTriggerNoTriggerMessages(
        description=LocalizedString('commands.admin.trigger_messages.configure.trigger.noTriggerMessages.description'),
        title=LocalizedString('commands.admin.trigger_messages.configure.trigger.noTriggerMessages.title'),
    )
    _n_commands_admin_trigger_messages_configure_trigger = CommandsAdminTrigger_messagesConfigureTrigger(
        addChannel=_n_commands_admin_trigger_messages_configure_trigger_addChannel,
        caseInsensitive=LocalizedString('commands.admin.trigger_messages.configure.trigger.caseInsensitive'),
        caseSensitive=LocalizedString('commands.admin.trigger_messages.configure.trigger.caseSensitive'),
        case_sensitive=LocalizedString('commands.admin.trigger_messages.configure.trigger.case_sensitive'),
        channels=LocalizedString('commands.admin.trigger_messages.configure.trigger.channels'),
        description=LocalizedString('commands.admin.trigger_messages.configure.trigger.description'),
        noChannels=LocalizedString('commands.admin.trigger_messages.configure.trigger.noChannels'),
        noTriggerMessages=_n_commands_admin_trigger_messages_configure_trigger_noTriggerMessages,
        title=LocalizedString('commands.admin.trigger_messages.configure.trigger.title'),
    )
    _n_commands_admin_trigger_messages_configure_up = CommandsAdminTrigger_messagesConfigureUp(
        label=LocalizedString('commands.admin.trigger_messages.configure.up.label'),
    )
    _n_commands_admin_trigger_messages_configure = CommandsAdminTrigger_messagesConfigure(
        add_channel=_n_commands_admin_trigger_messages_configure_add_channel,
        down=_n_commands_admin_trigger_messages_configure_down,
        missingPermission=_n_commands_admin_trigger_messages_configure_missingPermission,
        modal=_n_commands_admin_trigger_messages_configure_modal,
        new=_n_commands_admin_trigger_messages_configure_new,
        next=_n_commands_admin_trigger_messages_configure_next,
        noTriggerMessages=_n_commands_admin_trigger_messages_configure_noTriggerMessages,
        previous=_n_commands_admin_trigger_messages_configure_previous,
        remove=_n_commands_admin_trigger_messages_configure_remove,
        remove_channel=_n_commands_admin_trigger_messages_configure_remove_channel,
        trigger=_n_commands_admin_trigger_messages_configure_trigger,
        up=_n_commands_admin_trigger_messages_configure_up,
    )
    _n_commands_admin_trigger_messages = CommandsAdminTrigger_messages(
        add=_n_commands_admin_trigger_messages_add,
        configure=_n_commands_admin_trigger_messages_configure,
    )
    _n_commands_admin_unban_error = CommandsAdminUnbanError(
        description=LocalizedString('commands.admin.unban.error.description'),
        title=LocalizedString('commands.admin.unban.error.title'),
    )
    _n_commands_admin_unban_forbidden = CommandsAdminUnbanForbidden(
        description=LocalizedString('commands.admin.unban.forbidden.description'),
        title=LocalizedString('commands.admin.unban.forbidden.title'),
    )
    _n_commands_admin_unban_missingPermission = CommandsAdminUnbanMissingPermission(
        description=LocalizedString('commands.admin.unban.missingPermission.description'),
        title=LocalizedString('commands.admin.unban.missingPermission.title'),
    )
    _n_commands_admin_unban_missingPermissionBot = CommandsAdminUnbanMissingPermissionBot(
        description=LocalizedString('commands.admin.unban.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.unban.missingPermissionBot.title'),
    )
    _n_commands_admin_unban_success = CommandsAdminUnbanSuccess(
        description=LocalizedString('commands.admin.unban.success.description'),
        title=LocalizedString('commands.admin.unban.success.title'),
    )
    _n_commands_admin_unban_userNotFound = CommandsAdminUnbanUserNotFound(
        description=LocalizedString('commands.admin.unban.userNotFound.description'),
        title=LocalizedString('commands.admin.unban.userNotFound.title'),
    )
    _n_commands_admin_unban = CommandsAdminUnban(
        error=_n_commands_admin_unban_error,
        forbidden=_n_commands_admin_unban_forbidden,
        missingPermission=_n_commands_admin_unban_missingPermission,
        missingPermissionBot=_n_commands_admin_unban_missingPermissionBot,
        noReasonProvided=LocalizedString('commands.admin.unban.noReasonProvided'),
        success=_n_commands_admin_unban_success,
        userNotFound=_n_commands_admin_unban_userNotFound,
    )
    _n_commands_admin_unlock_error = CommandsAdminUnlockError(
        description=LocalizedString('commands.admin.unlock.error.description'),
        title=LocalizedString('commands.admin.unlock.error.title'),
    )
    _n_commands_admin_unlock_forbidden = CommandsAdminUnlockForbidden(
        description=LocalizedString('commands.admin.unlock.forbidden.description'),
        title=LocalizedString('commands.admin.unlock.forbidden.title'),
    )
    _n_commands_admin_unlock_missingPermission = CommandsAdminUnlockMissingPermission(
        description=LocalizedString('commands.admin.unlock.missingPermission.description'),
        title=LocalizedString('commands.admin.unlock.missingPermission.title'),
    )
    _n_commands_admin_unlock_missingPermissionBot = CommandsAdminUnlockMissingPermissionBot(
        description=LocalizedString('commands.admin.unlock.missingPermissionBot.description'),
        title=LocalizedString('commands.admin.unlock.missingPermissionBot.title'),
    )
    _n_commands_admin_unlock_notLocked = CommandsAdminUnlockNotLocked(
        description=LocalizedString('commands.admin.unlock.notLocked.description'),
        title=LocalizedString('commands.admin.unlock.notLocked.title'),
    )
    _n_commands_admin_unlock_success = CommandsAdminUnlockSuccess(
        description=LocalizedString('commands.admin.unlock.success.description'),
        title=LocalizedString('commands.admin.unlock.success.title'),
    )
    _n_commands_admin_unlock = CommandsAdminUnlock(
        channelUnlockedMessage=LocalizedString('commands.admin.unlock.channelUnlockedMessage'),
        error=_n_commands_admin_unlock_error,
        forbidden=_n_commands_admin_unlock_forbidden,
        missingPermission=_n_commands_admin_unlock_missingPermission,
        missingPermissionBot=_n_commands_admin_unlock_missingPermissionBot,
        notLocked=_n_commands_admin_unlock_notLocked,
        success=_n_commands_admin_unlock_success,
    )
    _n_commands_admin_update_text = CommandsAdminUpdate_text(
        cancelled=LocalizedString('commands.admin.update_text.cancelled'),
        confirm=LocalizedString('commands.admin.update_text.confirm'),
        confirm2=LocalizedString('commands.admin.update_text.confirm2'),
        enter_password=LocalizedString('commands.admin.update_text.enter_password'),
        expected_password=LocalizedString('commands.admin.update_text.expected_password'),
        say_wallah=LocalizedString('commands.admin.update_text.say_wallah'),
        timeout=LocalizedString('commands.admin.update_text.timeout'),
        wrong_password=LocalizedString('commands.admin.update_text.wrong_password'),
    )
    _n_commands_admin_viewwarns_missingPermission = CommandsAdminViewwarnsMissingPermission(
        description=LocalizedString('commands.admin.viewwarns.missingPermission.description'),
        title=LocalizedString('commands.admin.viewwarns.missingPermission.title'),
    )
    _n_commands_admin_viewwarns_noWarnings = CommandsAdminViewwarnsNoWarnings(
        description=LocalizedString('commands.admin.viewwarns.noWarnings.description'),
        title=LocalizedString('commands.admin.viewwarns.noWarnings.title'),
    )
    _n_commands_admin_viewwarns = CommandsAdminViewwarns(
        description=LocalizedString('commands.admin.viewwarns.description'),
        missingPermission=_n_commands_admin_viewwarns_missingPermission,
        never=LocalizedString('commands.admin.viewwarns.never'),
        nextButton=LocalizedString('commands.admin.viewwarns.nextButton'),
        noReason=LocalizedString('commands.admin.viewwarns.noReason'),
        noWarnings=_n_commands_admin_viewwarns_noWarnings,
        pageFooter=LocalizedString('commands.admin.viewwarns.pageFooter'),
        prevButton=LocalizedString('commands.admin.viewwarns.prevButton'),
        removeButton=LocalizedString('commands.admin.viewwarns.removeButton'),
        title=LocalizedString('commands.admin.viewwarns.title'),
        unauthorizedUser=LocalizedString('commands.admin.viewwarns.unauthorizedUser'),
        warningDetails=LocalizedString('commands.admin.viewwarns.warningDetails'),
        warningEntry=LocalizedString('commands.admin.viewwarns.warningEntry'),
    )
    _n_commands_admin_warn_dmNotification = CommandsAdminWarnDmNotification(
        description=LocalizedString('commands.admin.warn.dmNotification.description'),
        title=LocalizedString('commands.admin.warn.dmNotification.title'),
    )
    _n_commands_admin_warn_missingPermission = CommandsAdminWarnMissingPermission(
        description=LocalizedString('commands.admin.warn.missingPermission.description'),
        title=LocalizedString('commands.admin.warn.missingPermission.title'),
    )
    _n_commands_admin_warn_reason = CommandsAdminWarnReason(
        reached_warnings=LocalizedString('commands.admin.warn.reason.reached_warnings'),
    )
    _n_commands_admin_warn_success = CommandsAdminWarnSuccess(
        description=LocalizedString('commands.admin.warn.success.description'),
        title=LocalizedString('commands.admin.warn.success.title'),
    )
    _n_commands_admin_warn_targetTooHigh = CommandsAdminWarnTargetTooHigh(
        description=LocalizedString('commands.admin.warn.targetTooHigh.description'),
        title=LocalizedString('commands.admin.warn.targetTooHigh.title'),
    )
    _n_commands_admin_warn = CommandsAdminWarn(
        dmNotification=_n_commands_admin_warn_dmNotification,
        missingPermission=_n_commands_admin_warn_missingPermission,
        noReasonProvided=LocalizedString('commands.admin.warn.noReasonProvided'),
        reason=_n_commands_admin_warn_reason,
        success=_n_commands_admin_warn_success,
        targetTooHigh=_n_commands_admin_warn_targetTooHigh,
    )
    _n_commands_admin_warnconfig_currentConfig = CommandsAdminWarnconfigCurrentConfig(
        description=LocalizedString('commands.admin.warnconfig.currentConfig.description'),
        title=LocalizedString('commands.admin.warnconfig.currentConfig.title'),
    )
    _n_commands_admin_warnconfig_error = CommandsAdminWarnconfigError(
        invalidInput=LocalizedString('commands.admin.warnconfig.error.invalidInput'),
        title=LocalizedString('commands.admin.warnconfig.error.title'),
    )
    _n_commands_admin_warnconfig_missingPermission = CommandsAdminWarnconfigMissingPermission(
        description=LocalizedString('commands.admin.warnconfig.missingPermission.description'),
        title=LocalizedString('commands.admin.warnconfig.missingPermission.title'),
    )
    _n_commands_admin_warnconfig_modal_ban_threshold = CommandsAdminWarnconfigModalBan_threshold(
        label=LocalizedString('commands.admin.warnconfig.modal.ban_threshold.label'),
        placeholder=LocalizedString('commands.admin.warnconfig.modal.ban_threshold.placeholder'),
    )
    _n_commands_admin_warnconfig_modal_kick_threshold = CommandsAdminWarnconfigModalKick_threshold(
        label=LocalizedString('commands.admin.warnconfig.modal.kick_threshold.label'),
        placeholder=LocalizedString('commands.admin.warnconfig.modal.kick_threshold.placeholder'),
    )
    _n_commands_admin_warnconfig_modal_timeout_duration = CommandsAdminWarnconfigModalTimeout_duration(
        label=LocalizedString('commands.admin.warnconfig.modal.timeout_duration.label'),
        placeholder=LocalizedString('commands.admin.warnconfig.modal.timeout_duration.placeholder'),
    )
    _n_commands_admin_warnconfig_modal_timeout_threshold = CommandsAdminWarnconfigModalTimeout_threshold(
        label=LocalizedString('commands.admin.warnconfig.modal.timeout_threshold.label'),
        placeholder=LocalizedString('commands.admin.warnconfig.modal.timeout_threshold.placeholder'),
    )
    _n_commands_admin_warnconfig_modal_warnexpiration = CommandsAdminWarnconfigModalWarnexpiration(
        label=LocalizedString('commands.admin.warnconfig.modal.warnexpiration.label'),
        placeholder=LocalizedString('commands.admin.warnconfig.modal.warnexpiration.placeholder'),
    )
    _n_commands_admin_warnconfig_modal = CommandsAdminWarnconfigModal(
        ban_threshold=_n_commands_admin_warnconfig_modal_ban_threshold,
        kick_threshold=_n_commands_admin_warnconfig_modal_kick_threshold,
        timeout_duration=_n_commands_admin_warnconfig_modal_timeout_duration,
        timeout_threshold=_n_commands_admin_warnconfig_modal_timeout_threshold,
        title=LocalizedString('commands.admin.warnconfig.modal.title'),
        warnexpiration=_n_commands_admin_warnconfig_modal_warnexpiration,
    )
    _n_commands_admin_warnconfig_success = CommandsAdminWarnconfigSuccess(
        description=LocalizedString('commands.admin.warnconfig.success.description'),
        title=LocalizedString('commands.admin.warnconfig.success.title'),
    )
    _n_commands_admin_warnconfig = CommandsAdminWarnconfig(
        currentConfig=_n_commands_admin_warnconfig_currentConfig,
        error=_n_commands_admin_warnconfig_error,
        missingPermission=_n_commands_admin_warnconfig_missingPermission,
        modal=_n_commands_admin_warnconfig_modal,
        success=_n_commands_admin_warnconfig_success,
    )
    _n_commands_admin = CommandsAdmin(
        add_role=_n_commands_admin_add_role,
        addrole=_n_commands_admin_addrole,
        administration=_n_commands_admin_administration,
        ban=_n_commands_admin_ban,
        boosterRole=_n_commands_admin_boosterRole,
        channel=_n_commands_admin_channel,
        close_ticket=_n_commands_admin_close_ticket,
        copy7tv=_n_commands_admin_copy7tv,
        copyEmoji=_n_commands_admin_copyEmoji,
        copyrole=_n_commands_admin_copyrole,
        createEmoji=_n_commands_admin_createEmoji,
        create_ticket=_n_commands_admin_create_ticket,
        createrole=_n_commands_admin_createrole,
        database_sync=_n_commands_admin_database_sync,
        deleterole=_n_commands_admin_deleterole,
        demo_message=_n_commands_admin_demo_message,
        embed=_n_commands_admin_embed,
        feedback=_n_commands_admin_feedback,
        joinToCreateListener=_n_commands_admin_joinToCreateListener,
        jointocreatechannel=_n_commands_admin_jointocreatechannel,
        kick=_n_commands_admin_kick,
        lock=_n_commands_admin_lock,
        moverole=_n_commands_admin_moverole,
        nickname=_n_commands_admin_nickname,
        nuke=_n_commands_admin_nuke,
        open_ticket=_n_commands_admin_open_ticket,
        purge=_n_commands_admin_purge,
        remove_role=_n_commands_admin_remove_role,
        remove_timeout=_n_commands_admin_remove_timeout,
        removejointocreatechannel=_n_commands_admin_removejointocreatechannel,
        removerole=_n_commands_admin_removerole,
        reports=_n_commands_admin_reports,
        say=_n_commands_admin_say,
        setLocale=_n_commands_admin_setLocale,
        slowmode=_n_commands_admin_slowmode,
        sync=_n_commands_admin_sync,
        timeout=_n_commands_admin_timeout,
        trigger_messages=_n_commands_admin_trigger_messages,
        unban=_n_commands_admin_unban,
        unlock=_n_commands_admin_unlock,
        update_text=_n_commands_admin_update_text,
        viewwarns=_n_commands_admin_viewwarns,
        warn=_n_commands_admin_warn,
        warnconfig=_n_commands_admin_warnconfig,
    )
    _n_commands_ai_addcustom_alreadyexists = CommandsAiAddcustomAlreadyexists(
        description=LocalizedString('commands.ai.addcustom.alreadyexists.description'),
        title=LocalizedString('commands.ai.addcustom.alreadyexists.title'),
    )
    _n_commands_ai_addcustom_invalidfrequency_penalty = CommandsAiAddcustomInvalidfrequency_penalty(
        description=LocalizedString('commands.ai.addcustom.invalidfrequency_penalty.description'),
        title=LocalizedString('commands.ai.addcustom.invalidfrequency_penalty.title'),
    )
    _n_commands_ai_addcustom_invalidpresence_penalty = CommandsAiAddcustomInvalidpresence_penalty(
        description=LocalizedString('commands.ai.addcustom.invalidpresence_penalty.description'),
        title=LocalizedString('commands.ai.addcustom.invalidpresence_penalty.title'),
    )
    _n_commands_ai_addcustom_invalidtemperature = CommandsAiAddcustomInvalidtemperature(
        description=LocalizedString('commands.ai.addcustom.invalidtemperature.description'),
        title=LocalizedString('commands.ai.addcustom.invalidtemperature.title'),
    )
    _n_commands_ai_addcustom_invalidtop_p = CommandsAiAddcustomInvalidtop_p(
        description=LocalizedString('commands.ai.addcustom.invalidtop_p.description'),
        title=LocalizedString('commands.ai.addcustom.invalidtop_p.title'),
    )
    _n_commands_ai_addcustom_longname = CommandsAiAddcustomLongname(
        description=LocalizedString('commands.ai.addcustom.longname.description'),
        title=LocalizedString('commands.ai.addcustom.longname.title'),
    )
    _n_commands_ai_addcustom_longsituation = CommandsAiAddcustomLongsituation(
        description=LocalizedString('commands.ai.addcustom.longsituation.description'),
        title=LocalizedString('commands.ai.addcustom.longsituation.title'),
    )
    _n_commands_ai_addcustom_namealreadyexists = CommandsAiAddcustomNamealreadyexists(
        description=LocalizedString('commands.ai.addcustom.namealreadyexists.description'),
        title=LocalizedString('commands.ai.addcustom.namealreadyexists.title'),
    )
    _n_commands_ai_addcustom_notplus = CommandsAiAddcustomNotplus(
        description=LocalizedString('commands.ai.addcustom.notplus.description'),
        title=LocalizedString('commands.ai.addcustom.notplus.title'),
    )
    _n_commands_ai_addcustom_shortname = CommandsAiAddcustomShortname(
        description=LocalizedString('commands.ai.addcustom.shortname.description'),
        title=LocalizedString('commands.ai.addcustom.shortname.title'),
    )
    _n_commands_ai_addcustom_shortsituation = CommandsAiAddcustomShortsituation(
        description=LocalizedString('commands.ai.addcustom.shortsituation.description'),
        title=LocalizedString('commands.ai.addcustom.shortsituation.title'),
    )
    _n_commands_ai_addcustom_success = CommandsAiAddcustomSuccess(
        description=LocalizedString('commands.ai.addcustom.success.description'),
        title=LocalizedString('commands.ai.addcustom.success.title'),
    )
    _n_commands_ai_addcustom = CommandsAiAddcustom(
        alreadyexists=_n_commands_ai_addcustom_alreadyexists,
        invalidfrequency_penalty=_n_commands_ai_addcustom_invalidfrequency_penalty,
        invalidpresence_penalty=_n_commands_ai_addcustom_invalidpresence_penalty,
        invalidtemperature=_n_commands_ai_addcustom_invalidtemperature,
        invalidtop_p=_n_commands_ai_addcustom_invalidtop_p,
        longname=_n_commands_ai_addcustom_longname,
        longsituation=_n_commands_ai_addcustom_longsituation,
        namealreadyexists=_n_commands_ai_addcustom_namealreadyexists,
        notplus=_n_commands_ai_addcustom_notplus,
        shortname=_n_commands_ai_addcustom_shortname,
        shortsituation=_n_commands_ai_addcustom_shortsituation,
        success=_n_commands_ai_addcustom_success,
    )
    _n_commands_ai_approvecustom_success = CommandsAiApprovecustomSuccess(
        description=LocalizedString('commands.ai.approvecustom.success.description'),
        title=LocalizedString('commands.ai.approvecustom.success.title'),
    )
    _n_commands_ai_approvecustom = CommandsAiApprovecustom(
        success=_n_commands_ai_approvecustom_success,
    )
    _n_commands_ai_ask_error = CommandsAiAskError(
        description=LocalizedString('commands.ai.ask.error.description'),
        title=LocalizedString('commands.ai.ask.error.title'),
    )
    _n_commands_ai_ask_noapi = CommandsAiAskNoapi(
        description=LocalizedString('commands.ai.ask.noapi.description'),
        title=LocalizedString('commands.ai.ask.noapi.title'),
    )
    _n_commands_ai_ask_notoken = CommandsAiAskNotoken(
        description=LocalizedString('commands.ai.ask.notoken.description'),
        title=LocalizedString('commands.ai.ask.notoken.title'),
    )
    _n_commands_ai_ask_success = CommandsAiAskSuccess(
        footer=LocalizedString('commands.ai.ask.success.footer'),
        title=LocalizedString('commands.ai.ask.success.title'),
    )
    _n_commands_ai_ask = CommandsAiAsk(
        error=_n_commands_ai_ask_error,
        noapi=_n_commands_ai_ask_noapi,
        notoken=_n_commands_ai_ask_notoken,
        success=_n_commands_ai_ask_success,
    )
    _n_commands_ai_deletecustom_notfound = CommandsAiDeletecustomNotfound(
        description=LocalizedString('commands.ai.deletecustom.notfound.description'),
        title=LocalizedString('commands.ai.deletecustom.notfound.title'),
    )
    _n_commands_ai_deletecustom_success = CommandsAiDeletecustomSuccess(
        description=LocalizedString('commands.ai.deletecustom.success.description'),
        title=LocalizedString('commands.ai.deletecustom.success.title'),
    )
    _n_commands_ai_deletecustom = CommandsAiDeletecustom(
        notfound=_n_commands_ai_deletecustom_notfound,
        success=_n_commands_ai_deletecustom_success,
    )
    _n_commands_ai_dencustom_success = CommandsAiDencustomSuccess(
        description=LocalizedString('commands.ai.dencustom.success.description'),
        title=LocalizedString('commands.ai.dencustom.success.title'),
    )
    _n_commands_ai_dencustom = CommandsAiDencustom(
        success=_n_commands_ai_dencustom_success,
    )
    _n_commands_ai_tokens_success = CommandsAiTokensSuccess(
        description=LocalizedString('commands.ai.tokens.success.description'),
        title=LocalizedString('commands.ai.tokens.success.title'),
    )
    _n_commands_ai_tokens = CommandsAiTokens(
        success=_n_commands_ai_tokens_success,
    )
    _n_commands_ai = CommandsAi(
        addcustom=_n_commands_ai_addcustom,
        approvecustom=_n_commands_ai_approvecustom,
        ask=_n_commands_ai_ask,
        deletecustom=_n_commands_ai_deletecustom,
        dencustom=_n_commands_ai_dencustom,
        tokens=_n_commands_ai_tokens,
    )
    _n_commands_channel_dynamicslowmode_alreadySet = CommandsChannelDynamicslowmodeAlreadySet(
        description=LocalizedString('commands.channel.dynamicslowmode.alreadySet.description'),
        title=LocalizedString('commands.channel.dynamicslowmode.alreadySet.title'),
    )
    _n_commands_channel_dynamicslowmode_channels = CommandsChannelDynamicslowmodeChannels(
        description=LocalizedString('commands.channel.dynamicslowmode.channels.description'),
        title=LocalizedString('commands.channel.dynamicslowmode.channels.title'),
    )
    _n_commands_channel_dynamicslowmode_deleteSuccess = CommandsChannelDynamicslowmodeDeleteSuccess(
        description=LocalizedString('commands.channel.dynamicslowmode.deleteSuccess.description'),
        title=LocalizedString('commands.channel.dynamicslowmode.deleteSuccess.title'),
    )
    _n_commands_channel_dynamicslowmode_missingBotPermission = CommandsChannelDynamicslowmodeMissingBotPermission(
        description=LocalizedString('commands.channel.dynamicslowmode.missingBotPermission.description'),
        title=LocalizedString('commands.channel.dynamicslowmode.missingBotPermission.title'),
    )
    _n_commands_channel_dynamicslowmode_missingPermission = CommandsChannelDynamicslowmodeMissingPermission(
        description=LocalizedString('commands.channel.dynamicslowmode.missingPermission.description'),
        title=LocalizedString('commands.channel.dynamicslowmode.missingPermission.title'),
    )
    _n_commands_channel_dynamicslowmode_noChannels = CommandsChannelDynamicslowmodeNoChannels(
        description=LocalizedString('commands.channel.dynamicslowmode.noChannels.description'),
        title=LocalizedString('commands.channel.dynamicslowmode.noChannels.title'),
    )
    _n_commands_channel_dynamicslowmode_notSet = CommandsChannelDynamicslowmodeNotSet(
        description=LocalizedString('commands.channel.dynamicslowmode.notSet.description'),
        title=LocalizedString('commands.channel.dynamicslowmode.notSet.title'),
    )
    _n_commands_channel_dynamicslowmode_success = CommandsChannelDynamicslowmodeSuccess(
        description=LocalizedString('commands.channel.dynamicslowmode.success.description'),
        title=LocalizedString('commands.channel.dynamicslowmode.success.title'),
    )
    _n_commands_channel_dynamicslowmode = CommandsChannelDynamicslowmode(
        alreadySet=_n_commands_channel_dynamicslowmode_alreadySet,
        channels=_n_commands_channel_dynamicslowmode_channels,
        deleteSuccess=_n_commands_channel_dynamicslowmode_deleteSuccess,
        missingBotPermission=_n_commands_channel_dynamicslowmode_missingBotPermission,
        missingPermission=_n_commands_channel_dynamicslowmode_missingPermission,
        noChannels=_n_commands_channel_dynamicslowmode_noChannels,
        notSet=_n_commands_channel_dynamicslowmode_notSet,
        reason=LocalizedString('commands.channel.dynamicslowmode.reason'),
        resetReason=LocalizedString('commands.channel.dynamicslowmode.resetReason'),
        success=_n_commands_channel_dynamicslowmode_success,
    )
    _n_commands_channel = CommandsChannel(
        dynamicslowmode=_n_commands_channel_dynamicslowmode,
    )
    _n_commands_fun_boop = CommandsFunBoop(
        title=LocalizedString('commands.fun.boop.title'),
    )
    _n_commands_fun_hug = CommandsFunHug(
        title=LocalizedString('commands.fun.hug.title'),
    )
    _n_commands_fun_kiss = CommandsFunKiss(
        title=LocalizedString('commands.fun.kiss.title'),
    )
    _n_commands_fun_laugh = CommandsFunLaugh(
        title=LocalizedString('commands.fun.laugh.title'),
    )
    _n_commands_fun_pat = CommandsFunPat(
        title=LocalizedString('commands.fun.pat.title'),
    )
    _n_commands_fun_poke = CommandsFunPoke(
        title=LocalizedString('commands.fun.poke.title'),
    )
    _n_commands_fun_slap = CommandsFunSlap(
        title=LocalizedString('commands.fun.slap.title'),
    )
    _n_commands_fun_tickle = CommandsFunTickle(
        title=LocalizedString('commands.fun.tickle.title'),
    )
    _n_commands_fun_wave = CommandsFunWave(
        title=LocalizedString('commands.fun.wave.title'),
    )
    _n_commands_fun = CommandsFun(
        boop=_n_commands_fun_boop,
        hug=_n_commands_fun_hug,
        kiss=_n_commands_fun_kiss,
        laugh=_n_commands_fun_laugh,
        pat=_n_commands_fun_pat,
        poke=_n_commands_fun_poke,
        slap=_n_commands_fun_slap,
        tickle=_n_commands_fun_tickle,
        wave=_n_commands_fun_wave,
    )
    _n_commands_games_akinator = CommandsGamesAkinator(
        back=LocalizedString('commands.games.akinator.back'),
        description=LocalizedString('commands.games.akinator.description'),
        end=LocalizedString('commands.games.akinator.end'),
        idk=LocalizedString('commands.games.akinator.idk'),
        no=LocalizedString('commands.games.akinator.no'),
        no_answer=LocalizedString('commands.games.akinator.no_answer'),
        notYourGame=LocalizedString('commands.games.akinator.notYourGame'),
        probably=LocalizedString('commands.games.akinator.probably'),
        probably_not=LocalizedString('commands.games.akinator.probably_not'),
        result=LocalizedString('commands.games.akinator.result'),
        title=LocalizedString('commands.games.akinator.title'),
        yes=LocalizedString('commands.games.akinator.yes'),
    )
    _n_commands_games_battleship_error = CommandsGamesBattleshipError(
        invalidColumn=LocalizedString('commands.games.battleship.error.invalidColumn'),
        invalidCoordinate=LocalizedString('commands.games.battleship.error.invalidCoordinate'),
        invalidRow=LocalizedString('commands.games.battleship.error.invalidRow'),
    )
    _n_commands_games_battleship = CommandsGamesBattleship(
        alreadyAttacked=LocalizedString('commands.games.battleship.alreadyAttacked'),
        battleTitle=LocalizedString('commands.games.battleship.battleTitle'),
        currentTurn=LocalizedString('commands.games.battleship.currentTurn'),
        error=_n_commands_games_battleship_error,
        gameOver=LocalizedString('commands.games.battleship.gameOver'),
        helpAttackInstruction=LocalizedString('commands.games.battleship.helpAttackInstruction'),
        helpBoards=LocalizedString('commands.games.battleship.helpBoards'),
        helpCurrentTurn=LocalizedString('commands.games.battleship.helpCurrentTurn'),
        helpEnemyBoard=LocalizedString('commands.games.battleship.helpEnemyBoard'),
        helpGiveUp=LocalizedString('commands.games.battleship.helpGiveUp'),
        helpGiveUpInstruction=LocalizedString('commands.games.battleship.helpGiveUpInstruction'),
        helpPlayers=LocalizedString('commands.games.battleship.helpPlayers'),
        helpPlayersValue=LocalizedString('commands.games.battleship.helpPlayersValue'),
        helpTitle=LocalizedString('commands.games.battleship.helpTitle'),
        helpToAttack=LocalizedString('commands.games.battleship.helpToAttack'),
        helpYourBoard=LocalizedString('commands.games.battleship.helpYourBoard'),
        legend=LocalizedString('commands.games.battleship.legend'),
        notYourGame=LocalizedString('commands.games.battleship.notYourGame'),
        notYourTurn=LocalizedString('commands.games.battleship.notYourTurn'),
        placementDescription=LocalizedString('commands.games.battleship.placementDescription'),
        placementTitle=LocalizedString('commands.games.battleship.placementTitle'),
        winner=LocalizedString('commands.games.battleship.winner'),
    )
    _n_commands_games_connect4_error_no_plus = CommandsGamesConnect4ErrorNo_plus(
        description=LocalizedString('commands.games.connect4.error.no_plus.description'),
        title=LocalizedString('commands.games.connect4.error.no_plus.title'),
    )
    _n_commands_games_connect4_error = CommandsGamesConnect4Error(
        no_plus=_n_commands_games_connect4_error_no_plus,
    )
    _n_commands_games_connect4 = CommandsGamesConnect4(
        cellAlreadyTaken=LocalizedString('commands.games.connect4.cellAlreadyTaken'),
        currentTurn=LocalizedString('commands.games.connect4.currentTurn'),
        description=LocalizedString('commands.games.connect4.description'),
        descriptionBotEnemy=LocalizedString('commands.games.connect4.descriptionBotEnemy'),
        draw=LocalizedString('commands.games.connect4.draw'),
        drop=LocalizedString('commands.games.connect4.drop'),
        error=_n_commands_games_connect4_error,
        invalidMove=LocalizedString('commands.games.connect4.invalidMove'),
        notYourGame=LocalizedString('commands.games.connect4.notYourGame'),
        notYourTurn=LocalizedString('commands.games.connect4.notYourTurn'),
        title=LocalizedString('commands.games.connect4.title'),
        winner=LocalizedString('commands.games.connect4.winner'),
    )
    _n_commands_games_flagquiz_buttons = CommandsGamesFlagquizButtons(
        giveUp=LocalizedString('commands.games.flagquiz.buttons.giveUp'),
        guess=LocalizedString('commands.games.flagquiz.buttons.guess'),
        hint=LocalizedString('commands.games.flagquiz.buttons.hint'),
    )
    _n_commands_games_flagquiz_error = CommandsGamesFlagquizError(
        hintUsed=LocalizedString('commands.games.flagquiz.error.hintUsed'),
    )
    _n_commands_games_flagquiz_failure = CommandsGamesFlagquizFailure(
        description=LocalizedString('commands.games.flagquiz.failure.description'),
        title=LocalizedString('commands.games.flagquiz.failure.title'),
    )
    _n_commands_games_flagquiz_givenUp = CommandsGamesFlagquizGivenUp(
        description=LocalizedString('commands.games.flagquiz.givenUp.description'),
        title=LocalizedString('commands.games.flagquiz.givenUp.title'),
    )
    _n_commands_games_flagquiz_initial = CommandsGamesFlagquizInitial(
        description=LocalizedString('commands.games.flagquiz.initial.description'),
        title=LocalizedString('commands.games.flagquiz.initial.title'),
    )
    _n_commands_games_flagquiz_modal_input = CommandsGamesFlagquizModalInput(
        label=LocalizedString('commands.games.flagquiz.modal.input.label'),
        placeholder=LocalizedString('commands.games.flagquiz.modal.input.placeholder'),
    )
    _n_commands_games_flagquiz_modal = CommandsGamesFlagquizModal(
        input=_n_commands_games_flagquiz_modal_input,
        title=LocalizedString('commands.games.flagquiz.modal.title'),
    )
    _n_commands_games_flagquiz_success = CommandsGamesFlagquizSuccess(
        description=LocalizedString('commands.games.flagquiz.success.description'),
        title=LocalizedString('commands.games.flagquiz.success.title'),
    )
    _n_commands_games_flagquiz = CommandsGamesFlagquiz(
        buttons=_n_commands_games_flagquiz_buttons,
        description=LocalizedString('commands.games.flagquiz.description'),
        error=_n_commands_games_flagquiz_error,
        failure=_n_commands_games_flagquiz_failure,
        givenUp=_n_commands_games_flagquiz_givenUp,
        hint=LocalizedString('commands.games.flagquiz.hint'),
        initial=_n_commands_games_flagquiz_initial,
        modal=_n_commands_games_flagquiz_modal,
        notYourGame=LocalizedString('commands.games.flagquiz.notYourGame'),
        success=_n_commands_games_flagquiz_success,
        title=LocalizedString('commands.games.flagquiz.title'),
    )
    _n_commands_games_hangman_buttons = CommandsGamesHangmanButtons(
        giveUp=LocalizedString('commands.games.hangman.buttons.giveUp'),
        guess=LocalizedString('commands.games.hangman.buttons.guess'),
    )
    _n_commands_games_hangman_error = CommandsGamesHangmanError(
        description=LocalizedString('commands.games.hangman.error.description'),
        invalidInput=LocalizedString('commands.games.hangman.error.invalidInput'),
        title=LocalizedString('commands.games.hangman.error.title'),
    )
    _n_commands_games_hangman_failure = CommandsGamesHangmanFailure(
        description=LocalizedString('commands.games.hangman.failure.description'),
        title=LocalizedString('commands.games.hangman.failure.title'),
    )
    _n_commands_games_hangman_givenUp = CommandsGamesHangmanGivenUp(
        description=LocalizedString('commands.games.hangman.givenUp.description'),
        title=LocalizedString('commands.games.hangman.givenUp.title'),
    )
    _n_commands_games_hangman_initial = CommandsGamesHangmanInitial(
        description=LocalizedString('commands.games.hangman.initial.description'),
        title=LocalizedString('commands.games.hangman.initial.title'),
    )
    _n_commands_games_hangman_modal_input = CommandsGamesHangmanModalInput(
        label=LocalizedString('commands.games.hangman.modal.input.label'),
        placeholder=LocalizedString('commands.games.hangman.modal.input.placeholder'),
    )
    _n_commands_games_hangman_modal = CommandsGamesHangmanModal(
        input=_n_commands_games_hangman_modal_input,
        title=LocalizedString('commands.games.hangman.modal.title'),
    )
    _n_commands_games_hangman_success = CommandsGamesHangmanSuccess(
        description=LocalizedString('commands.games.hangman.success.description'),
        title=LocalizedString('commands.games.hangman.success.title'),
    )
    _n_commands_games_hangman_wrongGuess = CommandsGamesHangmanWrongGuess(
        description=LocalizedString('commands.games.hangman.wrongGuess.description'),
        title=LocalizedString('commands.games.hangman.wrongGuess.title'),
    )
    _n_commands_games_hangman = CommandsGamesHangman(
        buttons=_n_commands_games_hangman_buttons,
        description=LocalizedString('commands.games.hangman.description'),
        error=_n_commands_games_hangman_error,
        failure=_n_commands_games_hangman_failure,
        givenUp=_n_commands_games_hangman_givenUp,
        initial=_n_commands_games_hangman_initial,
        modal=_n_commands_games_hangman_modal,
        notYourGame=LocalizedString('commands.games.hangman.notYourGame'),
        success=_n_commands_games_hangman_success,
        title=LocalizedString('commands.games.hangman.title'),
        wrongGuess=_n_commands_games_hangman_wrongGuess,
    )
    _n_commands_games_memory = CommandsGamesMemory(
        game_over=LocalizedString('commands.games.memory.game_over'),
        match=LocalizedString('commands.games.memory.match'),
        no_match=LocalizedString('commands.games.memory.no_match'),
        not_your_game=LocalizedString('commands.games.memory.not_your_game'),
        pairs_found=LocalizedString('commands.games.memory.pairs_found'),
        player=LocalizedString('commands.games.memory.player'),
        rules_intro=LocalizedString('commands.games.memory.rules_intro'),
        select_first=LocalizedString('commands.games.memory.select_first'),
        select_second=LocalizedString('commands.games.memory.select_second'),
        title=LocalizedString('commands.games.memory.title'),
        turns=LocalizedString('commands.games.memory.turns'),
        win=LocalizedString('commands.games.memory.win'),
    )
    _n_commands_games_rps = CommandsGamesRps(
        description=LocalizedString('commands.games.rps.description'),
        draw=LocalizedString('commands.games.rps.draw'),
        drawDescription=LocalizedString('commands.games.rps.drawDescription'),
        lose=LocalizedString('commands.games.rps.lose'),
        loseDescription=LocalizedString('commands.games.rps.loseDescription'),
        notYourGame=LocalizedString('commands.games.rps.notYourGame'),
        paper=LocalizedString('commands.games.rps.paper'),
        rock=LocalizedString('commands.games.rps.rock'),
        scissors=LocalizedString('commands.games.rps.scissors'),
        title=LocalizedString('commands.games.rps.title'),
        win=LocalizedString('commands.games.rps.win'),
        winDescription=LocalizedString('commands.games.rps.winDescription'),
    )
    _n_commands_games_ticTacToe = CommandsGamesTicTacToe(
        cellAlreadyTaken=LocalizedString('commands.games.ticTacToe.cellAlreadyTaken'),
        currentTurn=LocalizedString('commands.games.ticTacToe.currentTurn'),
        description=LocalizedString('commands.games.ticTacToe.description'),
        descriptionBotEnemy=LocalizedString('commands.games.ticTacToe.descriptionBotEnemy'),
        draw=LocalizedString('commands.games.ticTacToe.draw'),
        invalidMove=LocalizedString('commands.games.ticTacToe.invalidMove'),
        notYourGame=LocalizedString('commands.games.ticTacToe.notYourGame'),
        notYourTurn=LocalizedString('commands.games.ticTacToe.notYourTurn'),
        title=LocalizedString('commands.games.ticTacToe.title'),
        winner=LocalizedString('commands.games.ticTacToe.winner'),
    )
    _n_commands_games_tic_tac_toe = CommandsGamesTic_tac_toe(
        cellAlreadyTaken=LocalizedString('commands.games.tic_tac_toe.cellAlreadyTaken'),
        currentTurn=LocalizedString('commands.games.tic_tac_toe.currentTurn'),
        description=LocalizedString('commands.games.tic_tac_toe.description'),
        descriptionBotEnemy=LocalizedString('commands.games.tic_tac_toe.descriptionBotEnemy'),
        draw=LocalizedString('commands.games.tic_tac_toe.draw'),
        invalidMove=LocalizedString('commands.games.tic_tac_toe.invalidMove'),
        notYourGame=LocalizedString('commands.games.tic_tac_toe.notYourGame'),
        notYourTurn=LocalizedString('commands.games.tic_tac_toe.notYourTurn'),
        title=LocalizedString('commands.games.tic_tac_toe.title'),
        winner=LocalizedString('commands.games.tic_tac_toe.winner'),
    )
    _n_commands_games_wordle_buttons = CommandsGamesWordleButtons(
        giveUp=LocalizedString('commands.games.wordle.buttons.giveUp'),
        guess=LocalizedString('commands.games.wordle.buttons.guess'),
        playHard=LocalizedString('commands.games.wordle.buttons.playHard'),
        playNormal=LocalizedString('commands.games.wordle.buttons.playNormal'),
    )
    _n_commands_games_wordle_error = CommandsGamesWordleError(
        description=LocalizedString('commands.games.wordle.error.description'),
        invalidInput=LocalizedString('commands.games.wordle.error.invalidInput'),
        title=LocalizedString('commands.games.wordle.error.title'),
    )
    _n_commands_games_wordle_failure = CommandsGamesWordleFailure(
        description=LocalizedString('commands.games.wordle.failure.description'),
        title=LocalizedString('commands.games.wordle.failure.title'),
    )
    _n_commands_games_wordle_givenUp = CommandsGamesWordleGivenUp(
        description=LocalizedString('commands.games.wordle.givenUp.description'),
        title=LocalizedString('commands.games.wordle.givenUp.title'),
    )
    _n_commands_games_wordle_hardMode = CommandsGamesWordleHardMode(
        title=LocalizedString('commands.games.wordle.hardMode.title'),
    )
    _n_commands_games_wordle_initial_descriptionextra = CommandsGamesWordleInitialDescriptionextra(
        ja=LocalizedString('commands.games.wordle.initial.descriptionextra.ja'),
    )
    _n_commands_games_wordle_initial = CommandsGamesWordleInitial(
        description=LocalizedString('commands.games.wordle.initial.description'),
        descriptionextra=_n_commands_games_wordle_initial_descriptionextra,
        title=LocalizedString('commands.games.wordle.initial.title'),
    )
    _n_commands_games_wordle_modal_input = CommandsGamesWordleModalInput(
        label=LocalizedString('commands.games.wordle.modal.input.label'),
        placeholder=LocalizedString('commands.games.wordle.modal.input.placeholder'),
    )
    _n_commands_games_wordle_modal = CommandsGamesWordleModal(
        input=_n_commands_games_wordle_modal_input,
        title=LocalizedString('commands.games.wordle.modal.title'),
    )
    _n_commands_games_wordle_pickMode = CommandsGamesWordlePickMode(
        description=LocalizedString('commands.games.wordle.pickMode.description'),
        title=LocalizedString('commands.games.wordle.pickMode.title'),
    )
    _n_commands_games_wordle_stats = CommandsGamesWordleStats(
        title=LocalizedString('commands.games.wordle.stats.title'),
    )
    _n_commands_games_wordle_success = CommandsGamesWordleSuccess(
        description=LocalizedString('commands.games.wordle.success.description'),
        title=LocalizedString('commands.games.wordle.success.title'),
    )
    _n_commands_games_wordle = CommandsGamesWordle(
        buttons=_n_commands_games_wordle_buttons,
        description=LocalizedString('commands.games.wordle.description'),
        error=_n_commands_games_wordle_error,
        failure=_n_commands_games_wordle_failure,
        givenUp=_n_commands_games_wordle_givenUp,
        hardMode=_n_commands_games_wordle_hardMode,
        initial=_n_commands_games_wordle_initial,
        modal=_n_commands_games_wordle_modal,
        notYourGame=LocalizedString('commands.games.wordle.notYourGame'),
        pickMode=_n_commands_games_wordle_pickMode,
        stats=_n_commands_games_wordle_stats,
        success=_n_commands_games_wordle_success,
        title=LocalizedString('commands.games.wordle.title'),
    )
    _n_commands_games = CommandsGames(
        akinator=_n_commands_games_akinator,
        battleship=_n_commands_games_battleship,
        connect4=_n_commands_games_connect4,
        flagquiz=_n_commands_games_flagquiz,
        hangman=_n_commands_games_hangman,
        memory=_n_commands_games_memory,
        rps=_n_commands_games_rps,
        ticTacToe=_n_commands_games_ticTacToe,
        tic_tac_toe=_n_commands_games_tic_tac_toe,
        wordle=_n_commands_games_wordle,
    )
    _n_commands_giveaway_add_blacklist_role_alreadyBlacklisted = CommandsGiveawayAdd_blacklist_roleAlreadyBlacklisted(
        description=LocalizedString('commands.giveaway.add_blacklist_role.alreadyBlacklisted.description'),
        title=LocalizedString('commands.giveaway.add_blacklist_role.alreadyBlacklisted.title'),
    )
    _n_commands_giveaway_add_blacklist_role_missingPermission = CommandsGiveawayAdd_blacklist_roleMissingPermission(
        description=LocalizedString('commands.giveaway.add_blacklist_role.missingPermission.description'),
        title=LocalizedString('commands.giveaway.add_blacklist_role.missingPermission.title'),
    )
    _n_commands_giveaway_add_blacklist_role_pro_required = CommandsGiveawayAdd_blacklist_rolePro_required(
        description=LocalizedString('commands.giveaway.add_blacklist_role.pro_required.description'),
        title=LocalizedString('commands.giveaway.add_blacklist_role.pro_required.title'),
    )
    _n_commands_giveaway_add_blacklist_role_success = CommandsGiveawayAdd_blacklist_roleSuccess(
        description=LocalizedString('commands.giveaway.add_blacklist_role.success.description'),
        title=LocalizedString('commands.giveaway.add_blacklist_role.success.title'),
    )
    _n_commands_giveaway_add_blacklist_role = CommandsGiveawayAdd_blacklist_role(
        alreadyBlacklisted=_n_commands_giveaway_add_blacklist_role_alreadyBlacklisted,
        missingPermission=_n_commands_giveaway_add_blacklist_role_missingPermission,
        pro_required=_n_commands_giveaway_add_blacklist_role_pro_required,
        success=_n_commands_giveaway_add_blacklist_role_success,
    )
    _n_commands_giveaway_add_blacklist_user_alreadyBlacklisted = CommandsGiveawayAdd_blacklist_userAlreadyBlacklisted(
        description=LocalizedString('commands.giveaway.add_blacklist_user.alreadyBlacklisted.description'),
        title=LocalizedString('commands.giveaway.add_blacklist_user.alreadyBlacklisted.title'),
    )
    _n_commands_giveaway_add_blacklist_user_missingPermission = CommandsGiveawayAdd_blacklist_userMissingPermission(
        description=LocalizedString('commands.giveaway.add_blacklist_user.missingPermission.description'),
        title=LocalizedString('commands.giveaway.add_blacklist_user.missingPermission.title'),
    )
    _n_commands_giveaway_add_blacklist_user_success = CommandsGiveawayAdd_blacklist_userSuccess(
        description=LocalizedString('commands.giveaway.add_blacklist_user.success.description'),
        title=LocalizedString('commands.giveaway.add_blacklist_user.success.title'),
    )
    _n_commands_giveaway_add_blacklist_user = CommandsGiveawayAdd_blacklist_user(
        alreadyBlacklisted=_n_commands_giveaway_add_blacklist_user_alreadyBlacklisted,
        missingPermission=_n_commands_giveaway_add_blacklist_user_missingPermission,
        success=_n_commands_giveaway_add_blacklist_user_success,
    )
    _n_commands_giveaway_builder_add_channel_requirement_v = CommandsGiveawayBuilderAdd_channel_requirementV(
        p=LocalizedString('commands.giveaway.builder.add_channel_requirement.v.p'),
        t=LocalizedString('commands.giveaway.builder.add_channel_requirement.v.t'),
    )
    _n_commands_giveaway_builder_add_channel_requirement_value = CommandsGiveawayBuilderAdd_channel_requirementValue(
        description=LocalizedString('commands.giveaway.builder.add_channel_requirement.value.description'),
        updated=LocalizedString('commands.giveaway.builder.add_channel_requirement.value.updated'),
    )
    _n_commands_giveaway_builder_add_channel_requirement = CommandsGiveawayBuilderAdd_channel_requirement(
        cancelled=LocalizedString('commands.giveaway.builder.add_channel_requirement.cancelled'),
        label=LocalizedString('commands.giveaway.builder.add_channel_requirement.label'),
        placeholder=LocalizedString('commands.giveaway.builder.add_channel_requirement.placeholder'),
        removed=LocalizedString('commands.giveaway.builder.add_channel_requirement.removed'),
        select=LocalizedString('commands.giveaway.builder.add_channel_requirement.select'),
        v=_n_commands_giveaway_builder_add_channel_requirement_v,
        value=_n_commands_giveaway_builder_add_channel_requirement_value,
    )
    _n_commands_giveaway_builder_change_winners = CommandsGiveawayBuilderChange_winners(
        description=LocalizedString('commands.giveaway.builder.change_winners.description'),
        label=LocalizedString('commands.giveaway.builder.change_winners.label'),
        placeholder=LocalizedString('commands.giveaway.builder.change_winners.placeholder'),
        title=LocalizedString('commands.giveaway.builder.change_winners.title'),
        updated=LocalizedString('commands.giveaway.builder.change_winners.updated'),
    )
    _n_commands_giveaway_builder_channel = CommandsGiveawayBuilderChannel(
        selected=LocalizedString('commands.giveaway.builder.channel.selected'),
    )
    _n_commands_giveaway_builder_custom_name = CommandsGiveawayBuilderCustom_name(
        description=LocalizedString('commands.giveaway.builder.custom_name.description'),
        label=LocalizedString('commands.giveaway.builder.custom_name.label'),
        placeholder=LocalizedString('commands.giveaway.builder.custom_name.placeholder'),
        title=LocalizedString('commands.giveaway.builder.custom_name.title'),
        updated=LocalizedString('commands.giveaway.builder.custom_name.updated'),
    )
    _n_commands_giveaway_builder_day_requirement = CommandsGiveawayBuilderDay_requirement(
        description=LocalizedString('commands.giveaway.builder.day_requirement.description'),
        label=LocalizedString('commands.giveaway.builder.day_requirement.label'),
        placeholder=LocalizedString('commands.giveaway.builder.day_requirement.placeholder'),
        title=LocalizedString('commands.giveaway.builder.day_requirement.title'),
        updated=LocalizedString('commands.giveaway.builder.day_requirement.updated'),
    )
    _n_commands_giveaway_builder_description = CommandsGiveawayBuilderDescription(
        timeout=LocalizedString('commands.giveaway.builder.description.timeout'),
        updated=LocalizedString('commands.giveaway.builder.description.updated'),
    )
    _n_commands_giveaway_builder_end_time = CommandsGiveawayBuilderEnd_time(
        description=LocalizedString('commands.giveaway.builder.end_time.description'),
        label=LocalizedString('commands.giveaway.builder.end_time.label'),
        placeholder=LocalizedString('commands.giveaway.builder.end_time.placeholder'),
        title=LocalizedString('commands.giveaway.builder.end_time.title'),
        updated=LocalizedString('commands.giveaway.builder.end_time.updated'),
    )
    _n_commands_giveaway_builder_message = CommandsGiveawayBuilderMessage(
        label=LocalizedString('commands.giveaway.builder.message.label'),
        timeout=LocalizedString('commands.giveaway.builder.message.timeout'),
        too_long=LocalizedString('commands.giveaway.builder.message.too_long'),
        updated=LocalizedString('commands.giveaway.builder.message.updated'),
    )
    _n_commands_giveaway_builder_modal = CommandsGiveawayBuilderModal(
        timeout=LocalizedString('commands.giveaway.builder.modal.timeout'),
    )
    _n_commands_giveaway_builder_new_message_requirement = CommandsGiveawayBuilderNew_message_requirement(
        description=LocalizedString('commands.giveaway.builder.new_message_requirement.description'),
        label=LocalizedString('commands.giveaway.builder.new_message_requirement.label'),
        placeholder=LocalizedString('commands.giveaway.builder.new_message_requirement.placeholder'),
        title=LocalizedString('commands.giveaway.builder.new_message_requirement.title'),
        updated=LocalizedString('commands.giveaway.builder.new_message_requirement.updated'),
    )
    _n_commands_giveaway_builder_price = CommandsGiveawayBuilderPrice(
        label=LocalizedString('commands.giveaway.builder.price.label'),
        timeout=LocalizedString('commands.giveaway.builder.price.timeout'),
        updated=LocalizedString('commands.giveaway.builder.price.updated'),
    )
    _n_commands_giveaway_builder_remove_channel_requirement = CommandsGiveawayBuilderRemove_channel_requirement(
        label=LocalizedString('commands.giveaway.builder.remove_channel_requirement.label'),
        placeholder=LocalizedString('commands.giveaway.builder.remove_channel_requirement.placeholder'),
        removed=LocalizedString('commands.giveaway.builder.remove_channel_requirement.removed'),
        select=LocalizedString('commands.giveaway.builder.remove_channel_requirement.select'),
    )
    _n_commands_giveaway_builder_role_requirement = CommandsGiveawayBuilderRole_requirement(
        cancelled=LocalizedString('commands.giveaway.builder.role_requirement.cancelled'),
        description=LocalizedString('commands.giveaway.builder.role_requirement.description'),
        label=LocalizedString('commands.giveaway.builder.role_requirement.label'),
        placeholder=LocalizedString('commands.giveaway.builder.role_requirement.placeholder'),
        pro=LocalizedString('commands.giveaway.builder.role_requirement.pro'),
        select=LocalizedString('commands.giveaway.builder.role_requirement.select'),
        title=LocalizedString('commands.giveaway.builder.role_requirement.title'),
        updated=LocalizedString('commands.giveaway.builder.role_requirement.updated'),
    )
    _n_commands_giveaway_builder_sponsor_select = CommandsGiveawayBuilderSponsorSelect(
        name=LocalizedString('commands.giveaway.builder.sponsor.select.name'),
        placeholder=LocalizedString('commands.giveaway.builder.sponsor.select.placeholder'),
    )
    _n_commands_giveaway_builder_sponsor = CommandsGiveawayBuilderSponsor(
        cancelled=LocalizedString('commands.giveaway.builder.sponsor.cancelled'),
        label=LocalizedString('commands.giveaway.builder.sponsor.label'),
        select=_n_commands_giveaway_builder_sponsor_select,
        selected=LocalizedString('commands.giveaway.builder.sponsor.selected'),
        updated=LocalizedString('commands.giveaway.builder.sponsor.updated'),
    )
    _n_commands_giveaway_builder_start_time = CommandsGiveawayBuilderStart_time(
        description=LocalizedString('commands.giveaway.builder.start_time.description'),
        label=LocalizedString('commands.giveaway.builder.start_time.label'),
        placeholder=LocalizedString('commands.giveaway.builder.start_time.placeholder'),
        title=LocalizedString('commands.giveaway.builder.start_time.title'),
        updated=LocalizedString('commands.giveaway.builder.start_time.updated'),
    )
    _n_commands_giveaway_builder_success = CommandsGiveawayBuilderSuccess(
        description=LocalizedString('commands.giveaway.builder.success.description'),
        title=LocalizedString('commands.giveaway.builder.success.title'),
    )
    _n_commands_giveaway_builder_voice_requirement = CommandsGiveawayBuilderVoice_requirement(
        description=LocalizedString('commands.giveaway.builder.voice_requirement.description'),
        label=LocalizedString('commands.giveaway.builder.voice_requirement.label'),
        placeholder=LocalizedString('commands.giveaway.builder.voice_requirement.placeholder'),
        title=LocalizedString('commands.giveaway.builder.voice_requirement.title'),
        updated=LocalizedString('commands.giveaway.builder.voice_requirement.updated'),
    )
    _n_commands_giveaway_builder_winner = CommandsGiveawayBuilderWinner(
        updated=LocalizedString('commands.giveaway.builder.winner.updated'),
    )
    _n_commands_giveaway_builder = CommandsGiveawayBuilder(
        add_channel_requirement=_n_commands_giveaway_builder_add_channel_requirement,
        cancel=LocalizedString('commands.giveaway.builder.cancel'),
        change_description=LocalizedString('commands.giveaway.builder.change_description'),
        change_winners=_n_commands_giveaway_builder_change_winners,
        channel=_n_commands_giveaway_builder_channel,
        channel_selected=LocalizedString('commands.giveaway.builder.channel_selected'),
        confirm=LocalizedString('commands.giveaway.builder.confirm'),
        custom_name=_n_commands_giveaway_builder_custom_name,
        day_requirement=_n_commands_giveaway_builder_day_requirement,
        description=_n_commands_giveaway_builder_description,
        end_time=_n_commands_giveaway_builder_end_time,
        enter_description=LocalizedString('commands.giveaway.builder.enter_description'),
        enter_message=LocalizedString('commands.giveaway.builder.enter_message'),
        enter_price=LocalizedString('commands.giveaway.builder.enter_price'),
        false=LocalizedString('commands.giveaway.builder.false'),
        loading=LocalizedString('commands.giveaway.builder.loading'),
        message=_n_commands_giveaway_builder_message,
        modal=_n_commands_giveaway_builder_modal,
        new_message_requirement=_n_commands_giveaway_builder_new_message_requirement,
        no_permission=LocalizedString('commands.giveaway.builder.no_permission'),
        none=LocalizedString('commands.giveaway.builder.none'),
        not_authorized=LocalizedString('commands.giveaway.builder.not_authorized'),
        preview=LocalizedString('commands.giveaway.builder.preview'),
        price=_n_commands_giveaway_builder_price,
        remove_channel_requirement=_n_commands_giveaway_builder_remove_channel_requirement,
        role_requirement=_n_commands_giveaway_builder_role_requirement,
        sponsor=_n_commands_giveaway_builder_sponsor,
        start_time=_n_commands_giveaway_builder_start_time,
        success=_n_commands_giveaway_builder_success,
        true=LocalizedString('commands.giveaway.builder.true'),
        voice_requirement=_n_commands_giveaway_builder_voice_requirement,
        winner=_n_commands_giveaway_builder_winner,
        winners=LocalizedString('commands.giveaway.builder.winners'),
        with_button=LocalizedString('commands.giveaway.builder.with_button'),
    )
    _n_commands_giveaway_editor_success = CommandsGiveawayEditorSuccess(
        description=LocalizedString('commands.giveaway.editor.success.description'),
        title=LocalizedString('commands.giveaway.editor.success.title'),
    )
    _n_commands_giveaway_editor = CommandsGiveawayEditor(
        loading=LocalizedString('commands.giveaway.editor.loading'),
        no_permission=LocalizedString('commands.giveaway.editor.no_permission'),
        not_authorized=LocalizedString('commands.giveaway.editor.not_authorized'),
        not_found=LocalizedString('commands.giveaway.editor.not_found'),
        pro_required=LocalizedString('commands.giveaway.editor.pro_required'),
        success=_n_commands_giveaway_editor_success,
    )
    _n_commands_giveaway_end_giveaway_deleted = CommandsGiveawayEnd_giveawayDeleted(
        description=LocalizedString('commands.giveaway.end_giveaway.deleted.description'),
        title=LocalizedString('commands.giveaway.end_giveaway.deleted.title'),
    )
    _n_commands_giveaway_end_giveaway_error_already_ended = CommandsGiveawayEnd_giveawayErrorAlready_ended(
        description=LocalizedString('commands.giveaway.end_giveaway.error.already_ended.description'),
        title=LocalizedString('commands.giveaway.end_giveaway.error.already_ended.title'),
    )
    _n_commands_giveaway_end_giveaway_error_invalid_message = CommandsGiveawayEnd_giveawayErrorInvalid_message(
        description=LocalizedString('commands.giveaway.end_giveaway.error.invalid_message.description'),
        title=LocalizedString('commands.giveaway.end_giveaway.error.invalid_message.title'),
    )
    _n_commands_giveaway_end_giveaway_error_missingPermission = CommandsGiveawayEnd_giveawayErrorMissingPermission(
        description=LocalizedString('commands.giveaway.end_giveaway.error.missingPermission.description'),
        title=LocalizedString('commands.giveaway.end_giveaway.error.missingPermission.title'),
    )
    _n_commands_giveaway_end_giveaway_error_no_permission = CommandsGiveawayEnd_giveawayErrorNo_permission(
        description=LocalizedString('commands.giveaway.end_giveaway.error.no_permission.description'),
        title=LocalizedString('commands.giveaway.end_giveaway.error.no_permission.title'),
    )
    _n_commands_giveaway_end_giveaway_error = CommandsGiveawayEnd_giveawayError(
        already_ended=_n_commands_giveaway_end_giveaway_error_already_ended,
        invalid_message=_n_commands_giveaway_end_giveaway_error_invalid_message,
        missingPermission=_n_commands_giveaway_end_giveaway_error_missingPermission,
        no_permission=_n_commands_giveaway_end_giveaway_error_no_permission,
    )
    _n_commands_giveaway_end_giveaway_success = CommandsGiveawayEnd_giveawaySuccess(
        description=LocalizedString('commands.giveaway.end_giveaway.success.description'),
        title=LocalizedString('commands.giveaway.end_giveaway.success.title'),
    )
    _n_commands_giveaway_end_giveaway = CommandsGiveawayEnd_giveaway(
        deleted=_n_commands_giveaway_end_giveaway_deleted,
        error=_n_commands_giveaway_end_giveaway_error,
        success=_n_commands_giveaway_end_giveaway_success,
    )
    _n_commands_giveaway_end_giveaway_command_deleted = CommandsGiveawayEnd_giveaway_commandDeleted(
        description=LocalizedString('commands.giveaway.end_giveaway_command.deleted.description'),
        title=LocalizedString('commands.giveaway.end_giveaway_command.deleted.title'),
    )
    _n_commands_giveaway_end_giveaway_command_error_alreadyEnded = CommandsGiveawayEnd_giveaway_commandErrorAlreadyEnded(
        description=LocalizedString('commands.giveaway.end_giveaway_command.error.alreadyEnded.description'),
        title=LocalizedString('commands.giveaway.end_giveaway_command.error.alreadyEnded.title'),
    )
    _n_commands_giveaway_end_giveaway_command_error_missingPermission = CommandsGiveawayEnd_giveaway_commandErrorMissingPermission(
        description=LocalizedString('commands.giveaway.end_giveaway_command.error.missingPermission.description'),
        title=LocalizedString('commands.giveaway.end_giveaway_command.error.missingPermission.title'),
    )
    _n_commands_giveaway_end_giveaway_command_error_notFound = CommandsGiveawayEnd_giveaway_commandErrorNotFound(
        description=LocalizedString('commands.giveaway.end_giveaway_command.error.notFound.description'),
        title=LocalizedString('commands.giveaway.end_giveaway_command.error.notFound.title'),
    )
    _n_commands_giveaway_end_giveaway_command_error = CommandsGiveawayEnd_giveaway_commandError(
        alreadyEnded=_n_commands_giveaway_end_giveaway_command_error_alreadyEnded,
        missingPermission=_n_commands_giveaway_end_giveaway_command_error_missingPermission,
        notFound=_n_commands_giveaway_end_giveaway_command_error_notFound,
    )
    _n_commands_giveaway_end_giveaway_command_success = CommandsGiveawayEnd_giveaway_commandSuccess(
        description=LocalizedString('commands.giveaway.end_giveaway_command.success.description'),
        title=LocalizedString('commands.giveaway.end_giveaway_command.success.title'),
    )
    _n_commands_giveaway_end_giveaway_command = CommandsGiveawayEnd_giveaway_command(
        deleted=_n_commands_giveaway_end_giveaway_command_deleted,
        error=_n_commands_giveaway_end_giveaway_command_error,
        success=_n_commands_giveaway_end_giveaway_command_success,
    )
    _n_commands_giveaway_endedGiveaway_no_participants = CommandsGiveawayEndedGiveawayNo_participants(
        description=LocalizedString('commands.giveaway.endedGiveaway.no_participants.description'),
        title=LocalizedString('commands.giveaway.endedGiveaway.no_participants.title'),
    )
    _n_commands_giveaway_endedGiveaway = CommandsGiveawayEndedGiveaway(
        button_text=LocalizedString('commands.giveaway.endedGiveaway.button_text'),
        description=LocalizedString('commands.giveaway.endedGiveaway.description'),
        dm=LocalizedString('commands.giveaway.endedGiveaway.dm'),
        no_participants=_n_commands_giveaway_endedGiveaway_no_participants,
        title=LocalizedString('commands.giveaway.endedGiveaway.title'),
        winnerDM=LocalizedString('commands.giveaway.endedGiveaway.winnerDM'),
    )
    _n_commands_giveaway_giveawayEmbed_participation_failed = CommandsGiveawayGiveawayEmbedParticipation_failed(
        blacklisted=LocalizedString('commands.giveaway.giveawayEmbed.participation_failed.blacklisted'),
        blacklisted_role=LocalizedString('commands.giveaway.giveawayEmbed.participation_failed.blacklisted_role'),
        channel_requirements=LocalizedString('commands.giveaway.giveawayEmbed.participation_failed.channel_requirements'),
        day_requirement=LocalizedString('commands.giveaway.giveawayEmbed.participation_failed.day_requirement'),
        message_requirement=LocalizedString('commands.giveaway.giveawayEmbed.participation_failed.message_requirement'),
        opted_out=LocalizedString('commands.giveaway.giveawayEmbed.participation_failed.opted_out'),
        role_requirement=LocalizedString('commands.giveaway.giveawayEmbed.participation_failed.role_requirement'),
        title=LocalizedString('commands.giveaway.giveawayEmbed.participation_failed.title'),
        voice_requirement=LocalizedString('commands.giveaway.giveawayEmbed.participation_failed.voice_requirement'),
    )
    _n_commands_giveaway_giveawayEmbed_participation_removed = CommandsGiveawayGiveawayEmbedParticipation_removed(
        description=LocalizedString('commands.giveaway.giveawayEmbed.participation_removed.description'),
        title=LocalizedString('commands.giveaway.giveawayEmbed.participation_removed.title'),
    )
    _n_commands_giveaway_giveawayEmbed_participation_success = CommandsGiveawayGiveawayEmbedParticipation_success(
        description=LocalizedString('commands.giveaway.giveawayEmbed.participation_success.description'),
        title=LocalizedString('commands.giveaway.giveawayEmbed.participation_success.title'),
    )
    _n_commands_giveaway_giveawayEmbed = CommandsGiveawayGiveawayEmbed(
        button_text=LocalizedString('commands.giveaway.giveawayEmbed.button_text'),
        channel_requirements=LocalizedString('commands.giveaway.giveawayEmbed.channel_requirements'),
        day_requirement=LocalizedString('commands.giveaway.giveawayEmbed.day_requirement'),
        description=LocalizedString('commands.giveaway.giveawayEmbed.description'),
        end_time=LocalizedString('commands.giveaway.giveawayEmbed.end_time'),
        footer=LocalizedString('commands.giveaway.giveawayEmbed.footer'),
        new_message_requirement=LocalizedString('commands.giveaway.giveawayEmbed.new_message_requirement'),
        no_requirements=LocalizedString('commands.giveaway.giveawayEmbed.no_requirements'),
        participation_failed=_n_commands_giveaway_giveawayEmbed_participation_failed,
        participation_removed=_n_commands_giveaway_giveawayEmbed_participation_removed,
        participation_success=_n_commands_giveaway_giveawayEmbed_participation_success,
        price=LocalizedString('commands.giveaway.giveawayEmbed.price'),
        role_requirement=LocalizedString('commands.giveaway.giveawayEmbed.role_requirement'),
        sponsor=LocalizedString('commands.giveaway.giveawayEmbed.sponsor'),
        title=LocalizedString('commands.giveaway.giveawayEmbed.title'),
        voice_requirement=LocalizedString('commands.giveaway.giveawayEmbed.voice_requirement'),
    )
    _n_commands_giveaway_list_blacklist_missingPermission = CommandsGiveawayList_blacklistMissingPermission(
        description=LocalizedString('commands.giveaway.list_blacklist.missingPermission.description'),
        title=LocalizedString('commands.giveaway.list_blacklist.missingPermission.title'),
    )
    _n_commands_giveaway_list_blacklist_noBlacklist = CommandsGiveawayList_blacklistNoBlacklist(
        description=LocalizedString('commands.giveaway.list_blacklist.noBlacklist.description'),
        title=LocalizedString('commands.giveaway.list_blacklist.noBlacklist.title'),
    )
    _n_commands_giveaway_list_blacklist = CommandsGiveawayList_blacklist(
        description=LocalizedString('commands.giveaway.list_blacklist.description'),
        empty=LocalizedString('commands.giveaway.list_blacklist.empty'),
        missingPermission=_n_commands_giveaway_list_blacklist_missingPermission,
        noBlacklist=_n_commands_giveaway_list_blacklist_noBlacklist,
        roles=LocalizedString('commands.giveaway.list_blacklist.roles'),
        title=LocalizedString('commands.giveaway.list_blacklist.title'),
        users=LocalizedString('commands.giveaway.list_blacklist.users'),
    )
    _n_commands_giveaway_remove_blacklist_role_missingPermission = CommandsGiveawayRemove_blacklist_roleMissingPermission(
        description=LocalizedString('commands.giveaway.remove_blacklist_role.missingPermission.description'),
        title=LocalizedString('commands.giveaway.remove_blacklist_role.missingPermission.title'),
    )
    _n_commands_giveaway_remove_blacklist_role_notBlacklisted = CommandsGiveawayRemove_blacklist_roleNotBlacklisted(
        description=LocalizedString('commands.giveaway.remove_blacklist_role.notBlacklisted.description'),
        title=LocalizedString('commands.giveaway.remove_blacklist_role.notBlacklisted.title'),
    )
    _n_commands_giveaway_remove_blacklist_role_success = CommandsGiveawayRemove_blacklist_roleSuccess(
        description=LocalizedString('commands.giveaway.remove_blacklist_role.success.description'),
        title=LocalizedString('commands.giveaway.remove_blacklist_role.success.title'),
    )
    _n_commands_giveaway_remove_blacklist_role = CommandsGiveawayRemove_blacklist_role(
        missingPermission=_n_commands_giveaway_remove_blacklist_role_missingPermission,
        notBlacklisted=_n_commands_giveaway_remove_blacklist_role_notBlacklisted,
        success=_n_commands_giveaway_remove_blacklist_role_success,
    )
    _n_commands_giveaway_remove_blacklist_user_missingPermission = CommandsGiveawayRemove_blacklist_userMissingPermission(
        description=LocalizedString('commands.giveaway.remove_blacklist_user.missingPermission.description'),
        title=LocalizedString('commands.giveaway.remove_blacklist_user.missingPermission.title'),
    )
    _n_commands_giveaway_remove_blacklist_user_notBlacklisted = CommandsGiveawayRemove_blacklist_userNotBlacklisted(
        description=LocalizedString('commands.giveaway.remove_blacklist_user.notBlacklisted.description'),
        title=LocalizedString('commands.giveaway.remove_blacklist_user.notBlacklisted.title'),
    )
    _n_commands_giveaway_remove_blacklist_user_success = CommandsGiveawayRemove_blacklist_userSuccess(
        description=LocalizedString('commands.giveaway.remove_blacklist_user.success.description'),
        title=LocalizedString('commands.giveaway.remove_blacklist_user.success.title'),
    )
    _n_commands_giveaway_remove_blacklist_user = CommandsGiveawayRemove_blacklist_user(
        missingPermission=_n_commands_giveaway_remove_blacklist_user_missingPermission,
        notBlacklisted=_n_commands_giveaway_remove_blacklist_user_notBlacklisted,
        success=_n_commands_giveaway_remove_blacklist_user_success,
    )
    _n_commands_giveaway_reroll_giveaway_error_missingPermission = CommandsGiveawayReroll_giveawayErrorMissingPermission(
        description=LocalizedString('commands.giveaway.reroll_giveaway.error.missingPermission.description'),
        title=LocalizedString('commands.giveaway.reroll_giveaway.error.missingPermission.title'),
    )
    _n_commands_giveaway_reroll_giveaway_error_noParticipants = CommandsGiveawayReroll_giveawayErrorNoParticipants(
        description=LocalizedString('commands.giveaway.reroll_giveaway.error.noParticipants.description'),
        title=LocalizedString('commands.giveaway.reroll_giveaway.error.noParticipants.title'),
    )
    _n_commands_giveaway_reroll_giveaway_error_notEnded = CommandsGiveawayReroll_giveawayErrorNotEnded(
        description=LocalizedString('commands.giveaway.reroll_giveaway.error.notEnded.description'),
        title=LocalizedString('commands.giveaway.reroll_giveaway.error.notEnded.title'),
    )
    _n_commands_giveaway_reroll_giveaway_error_notFound = CommandsGiveawayReroll_giveawayErrorNotFound(
        description=LocalizedString('commands.giveaway.reroll_giveaway.error.notFound.description'),
        title=LocalizedString('commands.giveaway.reroll_giveaway.error.notFound.title'),
    )
    _n_commands_giveaway_reroll_giveaway_error = CommandsGiveawayReroll_giveawayError(
        missingPermission=_n_commands_giveaway_reroll_giveaway_error_missingPermission,
        noParticipants=_n_commands_giveaway_reroll_giveaway_error_noParticipants,
        notAuthorized=LocalizedString('commands.giveaway.reroll_giveaway.error.notAuthorized'),
        notEnded=_n_commands_giveaway_reroll_giveaway_error_notEnded,
        notFound=_n_commands_giveaway_reroll_giveaway_error_notFound,
    )
    _n_commands_giveaway_reroll_giveaway_selectOption = CommandsGiveawayReroll_giveawaySelectOption(
        description=LocalizedString('commands.giveaway.reroll_giveaway.selectOption.description'),
        title=LocalizedString('commands.giveaway.reroll_giveaway.selectOption.title'),
    )
    _n_commands_giveaway_reroll_giveaway_success = CommandsGiveawayReroll_giveawaySuccess(
        description=LocalizedString('commands.giveaway.reroll_giveaway.success.description'),
        title=LocalizedString('commands.giveaway.reroll_giveaway.success.title'),
    )
    _n_commands_giveaway_reroll_giveaway = CommandsGiveawayReroll_giveaway(
        error=_n_commands_giveaway_reroll_giveaway_error,
        rerollAllWinners=LocalizedString('commands.giveaway.reroll_giveaway.rerollAllWinners'),
        rerollOneWinner=LocalizedString('commands.giveaway.reroll_giveaway.rerollOneWinner'),
        selectOption=_n_commands_giveaway_reroll_giveaway_selectOption,
        success=_n_commands_giveaway_reroll_giveaway_success,
        winnerDM=LocalizedString('commands.giveaway.reroll_giveaway.winnerDM'),
    )
    _n_commands_giveaway = CommandsGiveaway(
        add_blacklist_role=_n_commands_giveaway_add_blacklist_role,
        add_blacklist_user=_n_commands_giveaway_add_blacklist_user,
        builder=_n_commands_giveaway_builder,
        editor=_n_commands_giveaway_editor,
        end_giveaway=_n_commands_giveaway_end_giveaway,
        end_giveaway_command=_n_commands_giveaway_end_giveaway_command,
        endedGiveaway=_n_commands_giveaway_endedGiveaway,
        giveawayEmbed=_n_commands_giveaway_giveawayEmbed,
        list_blacklist=_n_commands_giveaway_list_blacklist,
        remove_blacklist_role=_n_commands_giveaway_remove_blacklist_role,
        remove_blacklist_user=_n_commands_giveaway_remove_blacklist_user,
        reroll_giveaway=_n_commands_giveaway_reroll_giveaway,
    )
    _n_commands_help_buttons = CommandsHelpButtons(
        next=LocalizedString('commands.help.buttons.next'),
        previous=LocalizedString('commands.help.buttons.previous'),
    )
    _n_commands_help_not_authorized = CommandsHelpNot_authorized(
        description=LocalizedString('commands.help.not_authorized.description'),
        title=LocalizedString('commands.help.not_authorized.title'),
    )
    _n_commands_help_select = CommandsHelpSelect(
        description=LocalizedString('commands.help.select.description'),
        placeholder=LocalizedString('commands.help.select.placeholder'),
        title=LocalizedString('commands.help.select.title'),
    )
    _n_commands_help_timeout = CommandsHelpTimeout(
        description=LocalizedString('commands.help.timeout.description'),
        title=LocalizedString('commands.help.timeout.title'),
    )
    _n_commands_help = CommandsHelp(
        buttons=_n_commands_help_buttons,
        not_authorized=_n_commands_help_not_authorized,
        select=_n_commands_help_select,
        timeout=_n_commands_help_timeout,
    )
    _n_commands_image_background_disabled = CommandsImageBackgroundDisabled(
        description=LocalizedString('commands.image.background.disabled.description'),
        title=LocalizedString('commands.image.background.disabled.title'),
    )
    _n_commands_image_background_success = CommandsImageBackgroundSuccess(
        description=LocalizedString('commands.image.background.success.description'),
        title=LocalizedString('commands.image.background.success.title'),
    )
    _n_commands_image_background = CommandsImageBackground(
        disabled=_n_commands_image_background_disabled,
        success=_n_commands_image_background_success,
    )
    _n_commands_image_blur_success = CommandsImageBlurSuccess(
        description=LocalizedString('commands.image.blur.success.description'),
        title=LocalizedString('commands.image.blur.success.title'),
    )
    _n_commands_image_blur = CommandsImageBlur(
        success=_n_commands_image_blur_success,
    )
    _n_commands_image_compress_success = CommandsImageCompressSuccess(
        description=LocalizedString('commands.image.compress.success.description'),
        title=LocalizedString('commands.image.compress.success.title'),
    )
    _n_commands_image_compress = CommandsImageCompress(
        success=_n_commands_image_compress_success,
    )
    _n_commands_image_contour_success = CommandsImageContourSuccess(
        description=LocalizedString('commands.image.contour.success.description'),
        title=LocalizedString('commands.image.contour.success.title'),
    )
    _n_commands_image_contour = CommandsImageContour(
        success=_n_commands_image_contour_success,
    )
    _n_commands_image_detail_success = CommandsImageDetailSuccess(
        description=LocalizedString('commands.image.detail.success.description'),
        title=LocalizedString('commands.image.detail.success.title'),
    )
    _n_commands_image_detail = CommandsImageDetail(
        success=_n_commands_image_detail_success,
    )
    _n_commands_image_edgeenhance_success = CommandsImageEdgeenhanceSuccess(
        description=LocalizedString('commands.image.edgeenhance.success.description'),
        title=LocalizedString('commands.image.edgeenhance.success.title'),
    )
    _n_commands_image_edgeenhance = CommandsImageEdgeenhance(
        success=_n_commands_image_edgeenhance_success,
    )
    _n_commands_image_emboss_success = CommandsImageEmbossSuccess(
        description=LocalizedString('commands.image.emboss.success.description'),
        title=LocalizedString('commands.image.emboss.success.title'),
    )
    _n_commands_image_emboss = CommandsImageEmboss(
        success=_n_commands_image_emboss_success,
    )
    _n_commands_image_error_unknown_filter = CommandsImageErrorUnknown_filter(
        description=LocalizedString('commands.image.error.unknown_filter.description'),
        title=LocalizedString('commands.image.error.unknown_filter.title'),
    )
    _n_commands_image_error = CommandsImageError(
        unknown_filter=_n_commands_image_error_unknown_filter,
    )
    _n_commands_image_filesize = CommandsImageFilesize(
        description=LocalizedString('commands.image.filesize.description'),
        title=LocalizedString('commands.image.filesize.title'),
    )
    _n_commands_image_findedges_success = CommandsImageFindedgesSuccess(
        description=LocalizedString('commands.image.findedges.success.description'),
        title=LocalizedString('commands.image.findedges.success.title'),
    )
    _n_commands_image_findedges = CommandsImageFindedges(
        success=_n_commands_image_findedges_success,
    )
    _n_commands_image_mirror_invalidaxis = CommandsImageMirrorInvalidaxis(
        description=LocalizedString('commands.image.mirror.invalidaxis.description'),
        title=LocalizedString('commands.image.mirror.invalidaxis.title'),
    )
    _n_commands_image_mirror_success = CommandsImageMirrorSuccess(
        description=LocalizedString('commands.image.mirror.success.description'),
        title=LocalizedString('commands.image.mirror.success.title'),
    )
    _n_commands_image_mirror = CommandsImageMirror(
        invalidaxis=_n_commands_image_mirror_invalidaxis,
        success=_n_commands_image_mirror_success,
    )
    _n_commands_image_rescale_success = CommandsImageRescaleSuccess(
        description=LocalizedString('commands.image.rescale.success.description'),
        title=LocalizedString('commands.image.rescale.success.title'),
    )
    _n_commands_image_rescale = CommandsImageRescale(
        success=_n_commands_image_rescale_success,
    )
    _n_commands_image_resize_success = CommandsImageResizeSuccess(
        description=LocalizedString('commands.image.resize.success.description'),
        title=LocalizedString('commands.image.resize.success.title'),
    )
    _n_commands_image_resize = CommandsImageResize(
        success=_n_commands_image_resize_success,
    )
    _n_commands_image_sharpen_success = CommandsImageSharpenSuccess(
        description=LocalizedString('commands.image.sharpen.success.description'),
        title=LocalizedString('commands.image.sharpen.success.title'),
    )
    _n_commands_image_sharpen = CommandsImageSharpen(
        success=_n_commands_image_sharpen_success,
    )
    _n_commands_image_smooth_success = CommandsImageSmoothSuccess(
        description=LocalizedString('commands.image.smooth.success.description'),
        title=LocalizedString('commands.image.smooth.success.title'),
    )
    _n_commands_image_smooth = CommandsImageSmooth(
        success=_n_commands_image_smooth_success,
    )
    _n_commands_image_typenotsupported = CommandsImageTypenotsupported(
        description=LocalizedString('commands.image.typenotsupported.description'),
        title=LocalizedString('commands.image.typenotsupported.title'),
    )
    _n_commands_image = CommandsImage(
        background=_n_commands_image_background,
        blur=_n_commands_image_blur,
        compress=_n_commands_image_compress,
        contour=_n_commands_image_contour,
        detail=_n_commands_image_detail,
        edgeenhance=_n_commands_image_edgeenhance,
        emboss=_n_commands_image_emboss,
        error=_n_commands_image_error,
        filesize=_n_commands_image_filesize,
        findedges=_n_commands_image_findedges,
        mirror=_n_commands_image_mirror,
        rescale=_n_commands_image_rescale,
        resize=_n_commands_image_resize,
        sharpen=_n_commands_image_sharpen,
        smooth=_n_commands_image_smooth,
        typenotsupported=_n_commands_image_typenotsupported,
    )
    _n_commands_level_addlevelrole_error_invalid_level = CommandsLevelAddlevelroleErrorInvalid_level(
        description=LocalizedString('commands.level.addlevelrole.error.invalid_level.description'),
        title=LocalizedString('commands.level.addlevelrole.error.invalid_level.title'),
    )
    _n_commands_level_addlevelrole_error_no_permission = CommandsLevelAddlevelroleErrorNo_permission(
        description=LocalizedString('commands.level.addlevelrole.error.no_permission.description'),
        title=LocalizedString('commands.level.addlevelrole.error.no_permission.title'),
    )
    _n_commands_level_addlevelrole_error_no_pro = CommandsLevelAddlevelroleErrorNo_pro(
        description=LocalizedString('commands.level.addlevelrole.error.no_pro.description'),
        title=LocalizedString('commands.level.addlevelrole.error.no_pro.title'),
    )
    _n_commands_level_addlevelrole_error_role_exists = CommandsLevelAddlevelroleErrorRole_exists(
        description=LocalizedString('commands.level.addlevelrole.error.role_exists.description'),
        title=LocalizedString('commands.level.addlevelrole.error.role_exists.title'),
    )
    _n_commands_level_addlevelrole_error = CommandsLevelAddlevelroleError(
        invalid_level=_n_commands_level_addlevelrole_error_invalid_level,
        no_permission=_n_commands_level_addlevelrole_error_no_permission,
        no_pro=_n_commands_level_addlevelrole_error_no_pro,
        role_exists=_n_commands_level_addlevelrole_error_role_exists,
    )
    _n_commands_level_addlevelrole_success = CommandsLevelAddlevelroleSuccess(
        description=LocalizedString('commands.level.addlevelrole.success.description'),
        title=LocalizedString('commands.level.addlevelrole.success.title'),
    )
    _n_commands_level_addlevelrole = CommandsLevelAddlevelrole(
        error=_n_commands_level_addlevelrole_error,
        success=_n_commands_level_addlevelrole_success,
    )
    _n_commands_level_blacklist_add_channel_error_no_permission = CommandsLevelBlacklistAdd_channelErrorNo_permission(
        description=LocalizedString('commands.level.blacklist.add_channel.error.no_permission.description'),
        title=LocalizedString('commands.level.blacklist.add_channel.error.no_permission.title'),
    )
    _n_commands_level_blacklist_add_channel_error_no_pro = CommandsLevelBlacklistAdd_channelErrorNo_pro(
        description=LocalizedString('commands.level.blacklist.add_channel.error.no_pro.description'),
        title=LocalizedString('commands.level.blacklist.add_channel.error.no_pro.title'),
    )
    _n_commands_level_blacklist_add_channel_error = CommandsLevelBlacklistAdd_channelError(
        no_permission=_n_commands_level_blacklist_add_channel_error_no_permission,
        no_pro=_n_commands_level_blacklist_add_channel_error_no_pro,
    )
    _n_commands_level_blacklist_add_channel_success = CommandsLevelBlacklistAdd_channelSuccess(
        description=LocalizedString('commands.level.blacklist.add_channel.success.description'),
        title=LocalizedString('commands.level.blacklist.add_channel.success.title'),
    )
    _n_commands_level_blacklist_add_channel = CommandsLevelBlacklistAdd_channel(
        error=_n_commands_level_blacklist_add_channel_error,
        success=_n_commands_level_blacklist_add_channel_success,
    )
    _n_commands_level_blacklist_add_role_error_no_permission = CommandsLevelBlacklistAdd_roleErrorNo_permission(
        description=LocalizedString('commands.level.blacklist.add_role.error.no_permission.description'),
        title=LocalizedString('commands.level.blacklist.add_role.error.no_permission.title'),
    )
    _n_commands_level_blacklist_add_role_error = CommandsLevelBlacklistAdd_roleError(
        no_permission=_n_commands_level_blacklist_add_role_error_no_permission,
    )
    _n_commands_level_blacklist_add_role_success = CommandsLevelBlacklistAdd_roleSuccess(
        description=LocalizedString('commands.level.blacklist.add_role.success.description'),
        title=LocalizedString('commands.level.blacklist.add_role.success.title'),
    )
    _n_commands_level_blacklist_add_role = CommandsLevelBlacklistAdd_role(
        error=_n_commands_level_blacklist_add_role_error,
        success=_n_commands_level_blacklist_add_role_success,
    )
    _n_commands_level_blacklist_add_user_error_no_permission = CommandsLevelBlacklistAdd_userErrorNo_permission(
        description=LocalizedString('commands.level.blacklist.add_user.error.no_permission.description'),
        title=LocalizedString('commands.level.blacklist.add_user.error.no_permission.title'),
    )
    _n_commands_level_blacklist_add_user_error = CommandsLevelBlacklistAdd_userError(
        no_permission=_n_commands_level_blacklist_add_user_error_no_permission,
    )
    _n_commands_level_blacklist_add_user_success = CommandsLevelBlacklistAdd_userSuccess(
        description=LocalizedString('commands.level.blacklist.add_user.success.description'),
        title=LocalizedString('commands.level.blacklist.add_user.success.title'),
    )
    _n_commands_level_blacklist_add_user = CommandsLevelBlacklistAdd_user(
        error=_n_commands_level_blacklist_add_user_error,
        success=_n_commands_level_blacklist_add_user_success,
    )
    _n_commands_level_blacklist_remove_channel_error_no_permission = CommandsLevelBlacklistRemove_channelErrorNo_permission(
        description=LocalizedString('commands.level.blacklist.remove_channel.error.no_permission.description'),
        title=LocalizedString('commands.level.blacklist.remove_channel.error.no_permission.title'),
    )
    _n_commands_level_blacklist_remove_channel_error = CommandsLevelBlacklistRemove_channelError(
        no_permission=_n_commands_level_blacklist_remove_channel_error_no_permission,
    )
    _n_commands_level_blacklist_remove_channel_success = CommandsLevelBlacklistRemove_channelSuccess(
        description=LocalizedString('commands.level.blacklist.remove_channel.success.description'),
        title=LocalizedString('commands.level.blacklist.remove_channel.success.title'),
    )
    _n_commands_level_blacklist_remove_channel = CommandsLevelBlacklistRemove_channel(
        error=_n_commands_level_blacklist_remove_channel_error,
        success=_n_commands_level_blacklist_remove_channel_success,
    )
    _n_commands_level_blacklist_remove_role_error_no_permission = CommandsLevelBlacklistRemove_roleErrorNo_permission(
        description=LocalizedString('commands.level.blacklist.remove_role.error.no_permission.description'),
        title=LocalizedString('commands.level.blacklist.remove_role.error.no_permission.title'),
    )
    _n_commands_level_blacklist_remove_role_error = CommandsLevelBlacklistRemove_roleError(
        no_permission=_n_commands_level_blacklist_remove_role_error_no_permission,
    )
    _n_commands_level_blacklist_remove_role_success = CommandsLevelBlacklistRemove_roleSuccess(
        description=LocalizedString('commands.level.blacklist.remove_role.success.description'),
        title=LocalizedString('commands.level.blacklist.remove_role.success.title'),
    )
    _n_commands_level_blacklist_remove_role = CommandsLevelBlacklistRemove_role(
        error=_n_commands_level_blacklist_remove_role_error,
        success=_n_commands_level_blacklist_remove_role_success,
    )
    _n_commands_level_blacklist_remove_user_error_no_permission = CommandsLevelBlacklistRemove_userErrorNo_permission(
        description=LocalizedString('commands.level.blacklist.remove_user.error.no_permission.description'),
        title=LocalizedString('commands.level.blacklist.remove_user.error.no_permission.title'),
    )
    _n_commands_level_blacklist_remove_user_error = CommandsLevelBlacklistRemove_userError(
        no_permission=_n_commands_level_blacklist_remove_user_error_no_permission,
    )
    _n_commands_level_blacklist_remove_user_success = CommandsLevelBlacklistRemove_userSuccess(
        description=LocalizedString('commands.level.blacklist.remove_user.success.description'),
        title=LocalizedString('commands.level.blacklist.remove_user.success.title'),
    )
    _n_commands_level_blacklist_remove_user = CommandsLevelBlacklistRemove_user(
        error=_n_commands_level_blacklist_remove_user_error,
        success=_n_commands_level_blacklist_remove_user_success,
    )
    _n_commands_level_blacklist_show_error_no_permission = CommandsLevelBlacklistShowErrorNo_permission(
        description=LocalizedString('commands.level.blacklist.show.error.no_permission.description'),
        title=LocalizedString('commands.level.blacklist.show.error.no_permission.title'),
    )
    _n_commands_level_blacklist_show_error = CommandsLevelBlacklistShowError(
        no_permission=_n_commands_level_blacklist_show_error_no_permission,
    )
    _n_commands_level_blacklist_show = CommandsLevelBlacklistShow(
        channels=LocalizedString('commands.level.blacklist.show.channels'),
        description=LocalizedString('commands.level.blacklist.show.description'),
        empty=LocalizedString('commands.level.blacklist.show.empty'),
        error=_n_commands_level_blacklist_show_error,
        roles=LocalizedString('commands.level.blacklist.show.roles'),
        title=LocalizedString('commands.level.blacklist.show.title'),
        users=LocalizedString('commands.level.blacklist.show.users'),
    )
    _n_commands_level_blacklist = CommandsLevelBlacklist(
        add_channel=_n_commands_level_blacklist_add_channel,
        add_role=_n_commands_level_blacklist_add_role,
        add_user=_n_commands_level_blacklist_add_user,
        no_reason=LocalizedString('commands.level.blacklist.no_reason'),
        remove_channel=_n_commands_level_blacklist_remove_channel,
        remove_role=_n_commands_level_blacklist_remove_role,
        remove_user=_n_commands_level_blacklist_remove_user,
        show=_n_commands_level_blacklist_show,
    )
    _n_commands_level_boosts_add_channel_success = CommandsLevelBoostsAdd_channelSuccess(
        description=LocalizedString('commands.level.boosts.add_channel.success.description'),
        title=LocalizedString('commands.level.boosts.add_channel.success.title'),
    )
    _n_commands_level_boosts_add_channel = CommandsLevelBoostsAdd_channel(
        success=_n_commands_level_boosts_add_channel_success,
    )
    _n_commands_level_boosts_add_role_success = CommandsLevelBoostsAdd_roleSuccess(
        description=LocalizedString('commands.level.boosts.add_role.success.description'),
        title=LocalizedString('commands.level.boosts.add_role.success.title'),
    )
    _n_commands_level_boosts_add_role = CommandsLevelBoostsAdd_role(
        success=_n_commands_level_boosts_add_role_success,
    )
    _n_commands_level_boosts_add_user_success = CommandsLevelBoostsAdd_userSuccess(
        description=LocalizedString('commands.level.boosts.add_user.success.description'),
        title=LocalizedString('commands.level.boosts.add_user.success.title'),
    )
    _n_commands_level_boosts_add_user = CommandsLevelBoostsAdd_user(
        success=_n_commands_level_boosts_add_user_success,
    )
    _n_commands_level_boosts_calculate_user_channel = CommandsLevelBoostsCalculate_user_channel(
        description=LocalizedString('commands.level.boosts.calculate_user_channel.description'),
        title=LocalizedString('commands.level.boosts.calculate_user_channel.title'),
    )
    _n_commands_level_boosts_error_no_pro = CommandsLevelBoostsErrorNo_pro(
        description=LocalizedString('commands.level.boosts.error.no_pro.description'),
        title=LocalizedString('commands.level.boosts.error.no_pro.title'),
    )
    _n_commands_level_boosts_error = CommandsLevelBoostsError(
        no_pro=_n_commands_level_boosts_error_no_pro,
    )
    _n_commands_level_boosts_remove_channel_success = CommandsLevelBoostsRemove_channelSuccess(
        description=LocalizedString('commands.level.boosts.remove_channel.success.description'),
        title=LocalizedString('commands.level.boosts.remove_channel.success.title'),
    )
    _n_commands_level_boosts_remove_channel = CommandsLevelBoostsRemove_channel(
        success=_n_commands_level_boosts_remove_channel_success,
    )
    _n_commands_level_boosts_remove_role_success = CommandsLevelBoostsRemove_roleSuccess(
        description=LocalizedString('commands.level.boosts.remove_role.success.description'),
        title=LocalizedString('commands.level.boosts.remove_role.success.title'),
    )
    _n_commands_level_boosts_remove_role = CommandsLevelBoostsRemove_role(
        success=_n_commands_level_boosts_remove_role_success,
    )
    _n_commands_level_boosts_remove_user_success = CommandsLevelBoostsRemove_userSuccess(
        description=LocalizedString('commands.level.boosts.remove_user.success.description'),
        title=LocalizedString('commands.level.boosts.remove_user.success.title'),
    )
    _n_commands_level_boosts_remove_user = CommandsLevelBoostsRemove_user(
        success=_n_commands_level_boosts_remove_user_success,
    )
    _n_commands_level_boosts_show = CommandsLevelBoostsShow(
        channels=LocalizedString('commands.level.boosts.show.channels'),
        description=LocalizedString('commands.level.boosts.show.description'),
        no_boosts=LocalizedString('commands.level.boosts.show.no_boosts'),
        roles=LocalizedString('commands.level.boosts.show.roles'),
        title=LocalizedString('commands.level.boosts.show.title'),
        users=LocalizedString('commands.level.boosts.show.users'),
    )
    _n_commands_level_boosts = CommandsLevelBoosts(
        add_channel=_n_commands_level_boosts_add_channel,
        add_role=_n_commands_level_boosts_add_role,
        add_user=_n_commands_level_boosts_add_user,
        additive=LocalizedString('commands.level.boosts.additive'),
        calculate_user_channel=_n_commands_level_boosts_calculate_user_channel,
        error=_n_commands_level_boosts_error,
        multiplicative=LocalizedString('commands.level.boosts.multiplicative'),
        remove_channel=_n_commands_level_boosts_remove_channel,
        remove_role=_n_commands_level_boosts_remove_role,
        remove_user=_n_commands_level_boosts_remove_user,
        show=_n_commands_level_boosts_show,
    )
    _n_commands_level_changelevelupmessage_error_message_too_long = CommandsLevelChangelevelupmessageErrorMessage_too_long(
        description=LocalizedString('commands.level.changelevelupmessage.error.message_too_long.description'),
        title=LocalizedString('commands.level.changelevelupmessage.error.message_too_long.title'),
    )
    _n_commands_level_changelevelupmessage_error_no_permission = CommandsLevelChangelevelupmessageErrorNo_permission(
        description=LocalizedString('commands.level.changelevelupmessage.error.no_permission.description'),
        title=LocalizedString('commands.level.changelevelupmessage.error.no_permission.title'),
    )
    _n_commands_level_changelevelupmessage_error_no_pro = CommandsLevelChangelevelupmessageErrorNo_pro(
        description=LocalizedString('commands.level.changelevelupmessage.error.no_pro.description'),
        title=LocalizedString('commands.level.changelevelupmessage.error.no_pro.title'),
    )
    _n_commands_level_changelevelupmessage_error = CommandsLevelChangelevelupmessageError(
        message_too_long=_n_commands_level_changelevelupmessage_error_message_too_long,
        no_permission=_n_commands_level_changelevelupmessage_error_no_permission,
        no_pro=_n_commands_level_changelevelupmessage_error_no_pro,
    )
    _n_commands_level_changelevelupmessage_success = CommandsLevelChangelevelupmessageSuccess(
        description=LocalizedString('commands.level.changelevelupmessage.success.description'),
        title=LocalizedString('commands.level.changelevelupmessage.success.title'),
    )
    _n_commands_level_changelevelupmessage = CommandsLevelChangelevelupmessage(
        error=_n_commands_level_changelevelupmessage_error,
        success=_n_commands_level_changelevelupmessage_success,
    )
    _n_commands_level_changexpscaling_error_invalid_scaling = CommandsLevelChangexpscalingErrorInvalid_scaling(
        description=LocalizedString('commands.level.changexpscaling.error.invalid_scaling.description'),
        title=LocalizedString('commands.level.changexpscaling.error.invalid_scaling.title'),
    )
    _n_commands_level_changexpscaling_error_no_custom_formula = CommandsLevelChangexpscalingErrorNo_custom_formula(
        description=LocalizedString('commands.level.changexpscaling.error.no_custom_formula.description'),
        title=LocalizedString('commands.level.changexpscaling.error.no_custom_formula.title'),
    )
    _n_commands_level_changexpscaling_error_no_permission = CommandsLevelChangexpscalingErrorNo_permission(
        description=LocalizedString('commands.level.changexpscaling.error.no_permission.description'),
        title=LocalizedString('commands.level.changexpscaling.error.no_permission.title'),
    )
    _n_commands_level_changexpscaling_error_no_pro = CommandsLevelChangexpscalingErrorNo_pro(
        description=LocalizedString('commands.level.changexpscaling.error.no_pro.description'),
        title=LocalizedString('commands.level.changexpscaling.error.no_pro.title'),
    )
    _n_commands_level_changexpscaling_error = CommandsLevelChangexpscalingError(
        invalid_scaling=_n_commands_level_changexpscaling_error_invalid_scaling,
        no_custom_formula=_n_commands_level_changexpscaling_error_no_custom_formula,
        no_permission=_n_commands_level_changexpscaling_error_no_permission,
        no_pro=_n_commands_level_changexpscaling_error_no_pro,
    )
    _n_commands_level_changexpscaling_formulas = CommandsLevelChangexpscalingFormulas(
        easy=LocalizedString('commands.level.changexpscaling.formulas.easy'),
        extreme=LocalizedString('commands.level.changexpscaling.formulas.extreme'),
        hard=LocalizedString('commands.level.changexpscaling.formulas.hard'),
        medium=LocalizedString('commands.level.changexpscaling.formulas.medium'),
    )
    _n_commands_level_changexpscaling_scalings = CommandsLevelChangexpscalingScalings(
        custom=LocalizedString('commands.level.changexpscaling.scalings.custom'),
        easy=LocalizedString('commands.level.changexpscaling.scalings.easy'),
        extreme=LocalizedString('commands.level.changexpscaling.scalings.extreme'),
        hard=LocalizedString('commands.level.changexpscaling.scalings.hard'),
        medium=LocalizedString('commands.level.changexpscaling.scalings.medium'),
    )
    _n_commands_level_changexpscaling_success = CommandsLevelChangexpscalingSuccess(
        description=LocalizedString('commands.level.changexpscaling.success.description'),
        title=LocalizedString('commands.level.changexpscaling.success.title'),
    )
    _n_commands_level_changexpscaling = CommandsLevelChangexpscaling(
        error=_n_commands_level_changexpscaling_error,
        formulas=_n_commands_level_changexpscaling_formulas,
        scalings=_n_commands_level_changexpscaling_scalings,
        success=_n_commands_level_changexpscaling_success,
        xp_examples=LocalizedString('commands.level.changexpscaling.xp_examples'),
    )
    _n_commands_level_disablelevelsystem_cancel = CommandsLevelDisablelevelsystemCancel(
        description=LocalizedString('commands.level.disablelevelsystem.cancel.description'),
        title=LocalizedString('commands.level.disablelevelsystem.cancel.title'),
    )
    _n_commands_level_disablelevelsystem_confirmation = CommandsLevelDisablelevelsystemConfirmation(
        description=LocalizedString('commands.level.disablelevelsystem.confirmation.description'),
        title=LocalizedString('commands.level.disablelevelsystem.confirmation.title'),
    )
    _n_commands_level_disablelevelsystem_error_already_disabled = CommandsLevelDisablelevelsystemErrorAlready_disabled(
        description=LocalizedString('commands.level.disablelevelsystem.error.already_disabled.description'),
        title=LocalizedString('commands.level.disablelevelsystem.error.already_disabled.title'),
    )
    _n_commands_level_disablelevelsystem_error_no_permission = CommandsLevelDisablelevelsystemErrorNo_permission(
        description=LocalizedString('commands.level.disablelevelsystem.error.no_permission.description'),
        title=LocalizedString('commands.level.disablelevelsystem.error.no_permission.title'),
    )
    _n_commands_level_disablelevelsystem_error = CommandsLevelDisablelevelsystemError(
        already_disabled=_n_commands_level_disablelevelsystem_error_already_disabled,
        no_permission=_n_commands_level_disablelevelsystem_error_no_permission,
    )
    _n_commands_level_disablelevelsystem_success = CommandsLevelDisablelevelsystemSuccess(
        description=LocalizedString('commands.level.disablelevelsystem.success.description'),
        title=LocalizedString('commands.level.disablelevelsystem.success.title'),
    )
    _n_commands_level_disablelevelsystem = CommandsLevelDisablelevelsystem(
        cancel=_n_commands_level_disablelevelsystem_cancel,
        confirm=LocalizedString('commands.level.disablelevelsystem.confirm'),
        confirmation=_n_commands_level_disablelevelsystem_confirmation,
        description=LocalizedString('commands.level.disablelevelsystem.description'),
        error=_n_commands_level_disablelevelsystem_error,
        name=LocalizedString('commands.level.disablelevelsystem.name'),
        success=_n_commands_level_disablelevelsystem_success,
    )
    _n_commands_level_disablelevelupmessage_error_already_disabled = CommandsLevelDisablelevelupmessageErrorAlready_disabled(
        description=LocalizedString('commands.level.disablelevelupmessage.error.already_disabled.description'),
        title=LocalizedString('commands.level.disablelevelupmessage.error.already_disabled.title'),
    )
    _n_commands_level_disablelevelupmessage_error_no_permission = CommandsLevelDisablelevelupmessageErrorNo_permission(
        description=LocalizedString('commands.level.disablelevelupmessage.error.no_permission.description'),
        title=LocalizedString('commands.level.disablelevelupmessage.error.no_permission.title'),
    )
    _n_commands_level_disablelevelupmessage_error_no_pro = CommandsLevelDisablelevelupmessageErrorNo_pro(
        description=LocalizedString('commands.level.disablelevelupmessage.error.no_pro.description'),
        title=LocalizedString('commands.level.disablelevelupmessage.error.no_pro.title'),
    )
    _n_commands_level_disablelevelupmessage_error = CommandsLevelDisablelevelupmessageError(
        already_disabled=_n_commands_level_disablelevelupmessage_error_already_disabled,
        no_permission=_n_commands_level_disablelevelupmessage_error_no_permission,
        no_pro=_n_commands_level_disablelevelupmessage_error_no_pro,
    )
    _n_commands_level_disablelevelupmessage_success = CommandsLevelDisablelevelupmessageSuccess(
        description=LocalizedString('commands.level.disablelevelupmessage.success.description'),
        title=LocalizedString('commands.level.disablelevelupmessage.success.title'),
    )
    _n_commands_level_disablelevelupmessage = CommandsLevelDisablelevelupmessage(
        error=_n_commands_level_disablelevelupmessage_error,
        success=_n_commands_level_disablelevelupmessage_success,
    )
    _n_commands_level_enablelevelsystem_error_already_enabled = CommandsLevelEnablelevelsystemErrorAlready_enabled(
        description=LocalizedString('commands.level.enablelevelsystem.error.already_enabled.description'),
        title=LocalizedString('commands.level.enablelevelsystem.error.already_enabled.title'),
    )
    _n_commands_level_enablelevelsystem_error_no_permission = CommandsLevelEnablelevelsystemErrorNo_permission(
        description=LocalizedString('commands.level.enablelevelsystem.error.no_permission.description'),
        title=LocalizedString('commands.level.enablelevelsystem.error.no_permission.title'),
    )
    _n_commands_level_enablelevelsystem_error = CommandsLevelEnablelevelsystemError(
        already_enabled=_n_commands_level_enablelevelsystem_error_already_enabled,
        no_permission=_n_commands_level_enablelevelsystem_error_no_permission,
    )
    _n_commands_level_enablelevelsystem_success = CommandsLevelEnablelevelsystemSuccess(
        description=LocalizedString('commands.level.enablelevelsystem.success.description'),
        title=LocalizedString('commands.level.enablelevelsystem.success.title'),
    )
    _n_commands_level_enablelevelsystem = CommandsLevelEnablelevelsystem(
        description=LocalizedString('commands.level.enablelevelsystem.description'),
        error=_n_commands_level_enablelevelsystem_error,
        name=LocalizedString('commands.level.enablelevelsystem.name'),
        success=_n_commands_level_enablelevelsystem_success,
    )
    _n_commands_level_enablelevelupmessage_error_already_enabled = CommandsLevelEnablelevelupmessageErrorAlready_enabled(
        description=LocalizedString('commands.level.enablelevelupmessage.error.already_enabled.description'),
        title=LocalizedString('commands.level.enablelevelupmessage.error.already_enabled.title'),
    )
    _n_commands_level_enablelevelupmessage_error_no_permission = CommandsLevelEnablelevelupmessageErrorNo_permission(
        description=LocalizedString('commands.level.enablelevelupmessage.error.no_permission.description'),
        title=LocalizedString('commands.level.enablelevelupmessage.error.no_permission.title'),
    )
    _n_commands_level_enablelevelupmessage_error_no_pro = CommandsLevelEnablelevelupmessageErrorNo_pro(
        description=LocalizedString('commands.level.enablelevelupmessage.error.no_pro.description'),
        title=LocalizedString('commands.level.enablelevelupmessage.error.no_pro.title'),
    )
    _n_commands_level_enablelevelupmessage_error = CommandsLevelEnablelevelupmessageError(
        already_enabled=_n_commands_level_enablelevelupmessage_error_already_enabled,
        no_permission=_n_commands_level_enablelevelupmessage_error_no_permission,
        no_pro=_n_commands_level_enablelevelupmessage_error_no_pro,
    )
    _n_commands_level_enablelevelupmessage_success = CommandsLevelEnablelevelupmessageSuccess(
        description=LocalizedString('commands.level.enablelevelupmessage.success.description'),
        title=LocalizedString('commands.level.enablelevelupmessage.success.title'),
    )
    _n_commands_level_enablelevelupmessage = CommandsLevelEnablelevelupmessage(
        error=_n_commands_level_enablelevelupmessage_error,
        success=_n_commands_level_enablelevelupmessage_success,
    )
    _n_commands_level_givexp_error_invalid_amount = CommandsLevelGivexpErrorInvalid_amount(
        description=LocalizedString('commands.level.givexp.error.invalid_amount.description'),
        title=LocalizedString('commands.level.givexp.error.invalid_amount.title'),
    )
    _n_commands_level_givexp_error_no_permission = CommandsLevelGivexpErrorNo_permission(
        description=LocalizedString('commands.level.givexp.error.no_permission.description'),
        title=LocalizedString('commands.level.givexp.error.no_permission.title'),
    )
    _n_commands_level_givexp_error = CommandsLevelGivexpError(
        invalid_amount=_n_commands_level_givexp_error_invalid_amount,
        no_permission=_n_commands_level_givexp_error_no_permission,
    )
    _n_commands_level_givexp_success = CommandsLevelGivexpSuccess(
        description=LocalizedString('commands.level.givexp.success.description'),
        title=LocalizedString('commands.level.givexp.success.title'),
    )
    _n_commands_level_givexp = CommandsLevelGivexp(
        error=_n_commands_level_givexp_error,
        success=_n_commands_level_givexp_success,
    )
    _n_commands_level_leaderboard = CommandsLevelLeaderboard(
        data=LocalizedString('commands.level.leaderboard.data'),
        next=LocalizedString('commands.level.leaderboard.next'),
        no_data=LocalizedString('commands.level.leaderboard.no_data'),
        notYourEmbed=LocalizedString('commands.level.leaderboard.notYourEmbed'),
        page=LocalizedString('commands.level.leaderboard.page'),
        previous=LocalizedString('commands.level.leaderboard.previous'),
        title=LocalizedString('commands.level.leaderboard.title'),
        titleNoPages=LocalizedString('commands.level.leaderboard.titleNoPages'),
    )
    _n_commands_level_rank_data = CommandsLevelRankData(
        level=LocalizedString('commands.level.rank.data.level'),
        xp=LocalizedString('commands.level.rank.data.xp'),
    )
    _n_commands_level_rank_error_no_data = CommandsLevelRankErrorNo_data(
        description=LocalizedString('commands.level.rank.error.no_data.description'),
        title=LocalizedString('commands.level.rank.error.no_data.title'),
    )
    _n_commands_level_rank_error = CommandsLevelRankError(
        no_data=_n_commands_level_rank_error_no_data,
    )
    _n_commands_level_rank_success = CommandsLevelRankSuccess(
        title=LocalizedString('commands.level.rank.success.title'),
    )
    _n_commands_level_rank = CommandsLevelRank(
        data=_n_commands_level_rank_data,
        error=_n_commands_level_rank_error,
        success=_n_commands_level_rank_success,
    )
    _n_commands_level_removelevelrole_error_no_permission = CommandsLevelRemovelevelroleErrorNo_permission(
        description=LocalizedString('commands.level.removelevelrole.error.no_permission.description'),
        title=LocalizedString('commands.level.removelevelrole.error.no_permission.title'),
    )
    _n_commands_level_removelevelrole_error_no_pro = CommandsLevelRemovelevelroleErrorNo_pro(
        description=LocalizedString('commands.level.removelevelrole.error.no_pro.description'),
        title=LocalizedString('commands.level.removelevelrole.error.no_pro.title'),
    )
    _n_commands_level_removelevelrole_error_role_not_found = CommandsLevelRemovelevelroleErrorRole_not_found(
        description=LocalizedString('commands.level.removelevelrole.error.role_not_found.description'),
        title=LocalizedString('commands.level.removelevelrole.error.role_not_found.title'),
    )
    _n_commands_level_removelevelrole_error = CommandsLevelRemovelevelroleError(
        no_permission=_n_commands_level_removelevelrole_error_no_permission,
        no_pro=_n_commands_level_removelevelrole_error_no_pro,
        role_not_found=_n_commands_level_removelevelrole_error_role_not_found,
    )
    _n_commands_level_removelevelrole_success = CommandsLevelRemovelevelroleSuccess(
        description=LocalizedString('commands.level.removelevelrole.success.description'),
        title=LocalizedString('commands.level.removelevelrole.success.title'),
    )
    _n_commands_level_removelevelrole = CommandsLevelRemovelevelrole(
        error=_n_commands_level_removelevelrole_error,
        success=_n_commands_level_removelevelrole_success,
    )
    _n_commands_level_setbackground_error_invalid_format = CommandsLevelSetbackgroundErrorInvalid_format(
        description=LocalizedString('commands.level.setbackground.error.invalid_format.description'),
        title=LocalizedString('commands.level.setbackground.error.invalid_format.title'),
    )
    _n_commands_level_setbackground_error_no_plus = CommandsLevelSetbackgroundErrorNo_plus(
        description=LocalizedString('commands.level.setbackground.error.no_plus.description'),
        title=LocalizedString('commands.level.setbackground.error.no_plus.title'),
    )
    _n_commands_level_setbackground_error = CommandsLevelSetbackgroundError(
        invalid_format=_n_commands_level_setbackground_error_invalid_format,
        no_plus=_n_commands_level_setbackground_error_no_plus,
    )
    _n_commands_level_setbackground_success = CommandsLevelSetbackgroundSuccess(
        description=LocalizedString('commands.level.setbackground.success.description'),
        title=LocalizedString('commands.level.setbackground.success.title'),
    )
    _n_commands_level_setbackground = CommandsLevelSetbackground(
        error=_n_commands_level_setbackground_error,
        success=_n_commands_level_setbackground_success,
    )
    _n_commands_level_setlevelupchannel_error_no_permission = CommandsLevelSetlevelupchannelErrorNo_permission(
        description=LocalizedString('commands.level.setlevelupchannel.error.no_permission.description'),
        title=LocalizedString('commands.level.setlevelupchannel.error.no_permission.title'),
    )
    _n_commands_level_setlevelupchannel_error_no_pro = CommandsLevelSetlevelupchannelErrorNo_pro(
        description=LocalizedString('commands.level.setlevelupchannel.error.no_pro.description'),
        title=LocalizedString('commands.level.setlevelupchannel.error.no_pro.title'),
    )
    _n_commands_level_setlevelupchannel_error = CommandsLevelSetlevelupchannelError(
        no_permission=_n_commands_level_setlevelupchannel_error_no_permission,
        no_pro=_n_commands_level_setlevelupchannel_error_no_pro,
    )
    _n_commands_level_setlevelupchannel_reset = CommandsLevelSetlevelupchannelReset(
        description=LocalizedString('commands.level.setlevelupchannel.reset.description'),
        title=LocalizedString('commands.level.setlevelupchannel.reset.title'),
    )
    _n_commands_level_setlevelupchannel_success = CommandsLevelSetlevelupchannelSuccess(
        description=LocalizedString('commands.level.setlevelupchannel.success.description'),
        title=LocalizedString('commands.level.setlevelupchannel.success.title'),
    )
    _n_commands_level_setlevelupchannel = CommandsLevelSetlevelupchannel(
        error=_n_commands_level_setlevelupchannel_error,
        reset=_n_commands_level_setlevelupchannel_reset,
        success=_n_commands_level_setlevelupchannel_success,
    )
    _n_commands_level_settextcooldown_error_invalid_cooldown = CommandsLevelSettextcooldownErrorInvalid_cooldown(
        description=LocalizedString('commands.level.settextcooldown.error.invalid_cooldown.description'),
        title=LocalizedString('commands.level.settextcooldown.error.invalid_cooldown.title'),
    )
    _n_commands_level_settextcooldown_error_no_permission = CommandsLevelSettextcooldownErrorNo_permission(
        description=LocalizedString('commands.level.settextcooldown.error.no_permission.description'),
        title=LocalizedString('commands.level.settextcooldown.error.no_permission.title'),
    )
    _n_commands_level_settextcooldown_error = CommandsLevelSettextcooldownError(
        invalid_cooldown=_n_commands_level_settextcooldown_error_invalid_cooldown,
        no_permission=_n_commands_level_settextcooldown_error_no_permission,
    )
    _n_commands_level_settextcooldown_params_cooldown = CommandsLevelSettextcooldownParamsCooldown(
        description=LocalizedString('commands.level.settextcooldown.params.cooldown.description'),
        name=LocalizedString('commands.level.settextcooldown.params.cooldown.name'),
    )
    _n_commands_level_settextcooldown_params = CommandsLevelSettextcooldownParams(
        cooldown=_n_commands_level_settextcooldown_params_cooldown,
    )
    _n_commands_level_settextcooldown_success = CommandsLevelSettextcooldownSuccess(
        description=LocalizedString('commands.level.settextcooldown.success.description'),
        title=LocalizedString('commands.level.settextcooldown.success.title'),
    )
    _n_commands_level_settextcooldown = CommandsLevelSettextcooldown(
        description=LocalizedString('commands.level.settextcooldown.description'),
        error=_n_commands_level_settextcooldown_error,
        name=LocalizedString('commands.level.settextcooldown.name'),
        params=_n_commands_level_settextcooldown_params,
        success=_n_commands_level_settextcooldown_success,
    )
    _n_commands_level_setvoicecooldown_error_invalid_cooldown = CommandsLevelSetvoicecooldownErrorInvalid_cooldown(
        description=LocalizedString('commands.level.setvoicecooldown.error.invalid_cooldown.description'),
        title=LocalizedString('commands.level.setvoicecooldown.error.invalid_cooldown.title'),
    )
    _n_commands_level_setvoicecooldown_error_no_permission = CommandsLevelSetvoicecooldownErrorNo_permission(
        description=LocalizedString('commands.level.setvoicecooldown.error.no_permission.description'),
        title=LocalizedString('commands.level.setvoicecooldown.error.no_permission.title'),
    )
    _n_commands_level_setvoicecooldown_error = CommandsLevelSetvoicecooldownError(
        invalid_cooldown=_n_commands_level_setvoicecooldown_error_invalid_cooldown,
        no_permission=_n_commands_level_setvoicecooldown_error_no_permission,
    )
    _n_commands_level_setvoicecooldown_params_cooldown = CommandsLevelSetvoicecooldownParamsCooldown(
        description=LocalizedString('commands.level.setvoicecooldown.params.cooldown.description'),
        name=LocalizedString('commands.level.setvoicecooldown.params.cooldown.name'),
    )
    _n_commands_level_setvoicecooldown_params = CommandsLevelSetvoicecooldownParams(
        cooldown=_n_commands_level_setvoicecooldown_params_cooldown,
    )
    _n_commands_level_setvoicecooldown_success = CommandsLevelSetvoicecooldownSuccess(
        description=LocalizedString('commands.level.setvoicecooldown.success.description'),
        title=LocalizedString('commands.level.setvoicecooldown.success.title'),
    )
    _n_commands_level_setvoicecooldown = CommandsLevelSetvoicecooldown(
        description=LocalizedString('commands.level.setvoicecooldown.description'),
        error=_n_commands_level_setvoicecooldown_error,
        name=LocalizedString('commands.level.setvoicecooldown.name'),
        params=_n_commands_level_setvoicecooldown_params,
        success=_n_commands_level_setvoicecooldown_success,
    )
    _n_commands_level_setxp_error_invalid_amount = CommandsLevelSetxpErrorInvalid_amount(
        description=LocalizedString('commands.level.setxp.error.invalid_amount.description'),
        title=LocalizedString('commands.level.setxp.error.invalid_amount.title'),
    )
    _n_commands_level_setxp_error_no_permission = CommandsLevelSetxpErrorNo_permission(
        description=LocalizedString('commands.level.setxp.error.no_permission.description'),
        title=LocalizedString('commands.level.setxp.error.no_permission.title'),
    )
    _n_commands_level_setxp_error = CommandsLevelSetxpError(
        invalid_amount=_n_commands_level_setxp_error_invalid_amount,
        no_permission=_n_commands_level_setxp_error_no_permission,
    )
    _n_commands_level_setxp_success = CommandsLevelSetxpSuccess(
        description=LocalizedString('commands.level.setxp.success.description'),
        title=LocalizedString('commands.level.setxp.success.title'),
    )
    _n_commands_level_setxp = CommandsLevelSetxp(
        error=_n_commands_level_setxp_error,
        success=_n_commands_level_setxp_success,
    )
    _n_commands_level_showlevelroles_add_role_modal = CommandsLevelShowlevelrolesAdd_role_modal(
        invalid_level=LocalizedString('commands.level.showlevelroles.add_role_modal.invalid_level'),
        level_label=LocalizedString('commands.level.showlevelroles.add_role_modal.level_label'),
        level_placeholder=LocalizedString('commands.level.showlevelroles.add_role_modal.level_placeholder'),
        success=LocalizedString('commands.level.showlevelroles.add_role_modal.success'),
        title=LocalizedString('commands.level.showlevelroles.add_role_modal.title'),
    )
    _n_commands_level_showlevelroles_error_no_permission = CommandsLevelShowlevelrolesErrorNo_permission(
        description=LocalizedString('commands.level.showlevelroles.error.no_permission.description'),
        title=LocalizedString('commands.level.showlevelroles.error.no_permission.title'),
    )
    _n_commands_level_showlevelroles_error_no_pro = CommandsLevelShowlevelrolesErrorNo_pro(
        description=LocalizedString('commands.level.showlevelroles.error.no_pro.description'),
        title=LocalizedString('commands.level.showlevelroles.error.no_pro.title'),
    )
    _n_commands_level_showlevelroles_error = CommandsLevelShowlevelrolesError(
        no_permission=_n_commands_level_showlevelroles_error_no_permission,
        no_pro=_n_commands_level_showlevelroles_error_no_pro,
    )
    _n_commands_level_showlevelroles_no_roles = CommandsLevelShowlevelrolesNo_roles(
        description=LocalizedString('commands.level.showlevelroles.no_roles.description'),
        title=LocalizedString('commands.level.showlevelroles.no_roles.title'),
    )
    _n_commands_level_showlevelroles_remove_role_confirm = CommandsLevelShowlevelrolesRemove_role_confirm(
        cancel_button=LocalizedString('commands.level.showlevelroles.remove_role_confirm.cancel_button'),
        confirm_button=LocalizedString('commands.level.showlevelroles.remove_role_confirm.confirm_button'),
    )
    _n_commands_level_showlevelroles_selected_level = CommandsLevelShowlevelrolesSelected_level(
        description=LocalizedString('commands.level.showlevelroles.selected_level.description'),
        title=LocalizedString('commands.level.showlevelroles.selected_level.title'),
    )
    _n_commands_level_showlevelroles = CommandsLevelShowlevelroles(
        add_button=LocalizedString('commands.level.showlevelroles.add_button'),
        add_role_cancelled=LocalizedString('commands.level.showlevelroles.add_role_cancelled'),
        add_role_modal=_n_commands_level_showlevelroles_add_role_modal,
        add_role_prompt=LocalizedString('commands.level.showlevelroles.add_role_prompt'),
        cancel_button=LocalizedString('commands.level.showlevelroles.cancel_button'),
        data=LocalizedString('commands.level.showlevelroles.data'),
        description=LocalizedString('commands.level.showlevelroles.description'),
        error=_n_commands_level_showlevelroles_error,
        level=LocalizedString('commands.level.showlevelroles.level'),
        next_button=LocalizedString('commands.level.showlevelroles.next_button'),
        no_roles=_n_commands_level_showlevelroles_no_roles,
        previous_button=LocalizedString('commands.level.showlevelroles.previous_button'),
        remove_button=LocalizedString('commands.level.showlevelroles.remove_button'),
        remove_role_cancelled=LocalizedString('commands.level.showlevelroles.remove_role_cancelled'),
        remove_role_confirm=_n_commands_level_showlevelroles_remove_role_confirm,
        remove_role_data=LocalizedString('commands.level.showlevelroles.remove_role_data'),
        remove_role_prompt=LocalizedString('commands.level.showlevelroles.remove_role_prompt'),
        remove_role_select_placeholder=LocalizedString('commands.level.showlevelroles.remove_role_select_placeholder'),
        remove_role_success=LocalizedString('commands.level.showlevelroles.remove_role_success'),
        role_select_placeholder=LocalizedString('commands.level.showlevelroles.role_select_placeholder'),
        select_placeholder=LocalizedString('commands.level.showlevelroles.select_placeholder'),
        selected_level=_n_commands_level_showlevelroles_selected_level,
        title=LocalizedString('commands.level.showlevelroles.title'),
    )
    _n_commands_level_showxpscalings = CommandsLevelShowxpscalings(
        data=LocalizedString('commands.level.showxpscalings.data'),
        description=LocalizedString('commands.level.showxpscalings.description'),
        title=LocalizedString('commands.level.showxpscalings.title'),
    )
    _n_commands_level_takexp_error_invalid_amount = CommandsLevelTakexpErrorInvalid_amount(
        description=LocalizedString('commands.level.takexp.error.invalid_amount.description'),
        title=LocalizedString('commands.level.takexp.error.invalid_amount.title'),
    )
    _n_commands_level_takexp_error_no_permission = CommandsLevelTakexpErrorNo_permission(
        description=LocalizedString('commands.level.takexp.error.no_permission.description'),
        title=LocalizedString('commands.level.takexp.error.no_permission.title'),
    )
    _n_commands_level_takexp_error = CommandsLevelTakexpError(
        invalid_amount=_n_commands_level_takexp_error_invalid_amount,
        no_permission=_n_commands_level_takexp_error_no_permission,
    )
    _n_commands_level_takexp_success = CommandsLevelTakexpSuccess(
        description=LocalizedString('commands.level.takexp.success.description'),
        title=LocalizedString('commands.level.takexp.success.title'),
    )
    _n_commands_level_takexp = CommandsLevelTakexp(
        error=_n_commands_level_takexp_error,
        success=_n_commands_level_takexp_success,
    )
    _n_commands_level_updateuserroles = CommandsLevelUpdateuserroles(
        reason=LocalizedString('commands.level.updateuserroles.reason'),
    )
    _n_commands_level = CommandsLevel(
        addlevelrole=_n_commands_level_addlevelrole,
        blacklist=_n_commands_level_blacklist,
        boosts=_n_commands_level_boosts,
        changelevelupmessage=_n_commands_level_changelevelupmessage,
        changexpscaling=_n_commands_level_changexpscaling,
        defaultlevelupmessage=LocalizedString('commands.level.defaultlevelupmessage'),
        disablelevelsystem=_n_commands_level_disablelevelsystem,
        disablelevelupmessage=_n_commands_level_disablelevelupmessage,
        enablelevelsystem=_n_commands_level_enablelevelsystem,
        enablelevelupmessage=_n_commands_level_enablelevelupmessage,
        givexp=_n_commands_level_givexp,
        leaderboard=_n_commands_level_leaderboard,
        rank=_n_commands_level_rank,
        removelevelrole=_n_commands_level_removelevelrole,
        setbackground=_n_commands_level_setbackground,
        setlevelupchannel=_n_commands_level_setlevelupchannel,
        settextcooldown=_n_commands_level_settextcooldown,
        setvoicecooldown=_n_commands_level_setvoicecooldown,
        setxp=_n_commands_level_setxp,
        showlevelroles=_n_commands_level_showlevelroles,
        showxpscalings=_n_commands_level_showxpscalings,
        takexp=_n_commands_level_takexp,
        updateuserroles=_n_commands_level_updateuserroles,
    )
    _n_commands_logs_blacklist_add_params_channel = CommandsLogsBlacklistAddParamsChannel(
        description=LocalizedString('commands.logs.blacklist.add.params.channel.description'),
    )
    _n_commands_logs_blacklist_add_params = CommandsLogsBlacklistAddParams(
        channel=_n_commands_logs_blacklist_add_params_channel,
    )
    _n_commands_logs_blacklist_add = CommandsLogsBlacklistAdd(
        description=LocalizedString('commands.logs.blacklist.add.description'),
        name=LocalizedString('commands.logs.blacklist.add.name'),
        params=_n_commands_logs_blacklist_add_params,
    )
    _n_commands_logs_blacklist_remove_params_channel = CommandsLogsBlacklistRemoveParamsChannel(
        description=LocalizedString('commands.logs.blacklist.remove.params.channel.description'),
    )
    _n_commands_logs_blacklist_remove_params = CommandsLogsBlacklistRemoveParams(
        channel=_n_commands_logs_blacklist_remove_params_channel,
    )
    _n_commands_logs_blacklist_remove = CommandsLogsBlacklistRemove(
        description=LocalizedString('commands.logs.blacklist.remove.description'),
        name=LocalizedString('commands.logs.blacklist.remove.name'),
        params=_n_commands_logs_blacklist_remove_params,
    )
    _n_commands_logs_blacklist_show = CommandsLogsBlacklistShow(
        description=LocalizedString('commands.logs.blacklist.show.description'),
        name=LocalizedString('commands.logs.blacklist.show.name'),
    )
    _n_commands_logs_blacklist = CommandsLogsBlacklist(
        add=_n_commands_logs_blacklist_add,
        description=LocalizedString('commands.logs.blacklist.description'),
        name=LocalizedString('commands.logs.blacklist.name'),
        remove=_n_commands_logs_blacklist_remove,
        show=_n_commands_logs_blacklist_show,
    )
    _n_commands_logs_blacklistCategory_alreadyBlacklisted = CommandsLogsBlacklistCategoryAlreadyBlacklisted(
        description=LocalizedString('commands.logs.blacklistCategory.alreadyBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistCategory.alreadyBlacklisted.title'),
    )
    _n_commands_logs_blacklistCategory_blacklisted = CommandsLogsBlacklistCategoryBlacklisted(
        description=LocalizedString('commands.logs.blacklistCategory.blacklisted.description'),
        title=LocalizedString('commands.logs.blacklistCategory.blacklisted.title'),
    )
    _n_commands_logs_blacklistCategory_missingChannel = CommandsLogsBlacklistCategoryMissingChannel(
        description=LocalizedString('commands.logs.blacklistCategory.missingChannel.description'),
        title=LocalizedString('commands.logs.blacklistCategory.missingChannel.title'),
    )
    _n_commands_logs_blacklistCategory_missingPermission = CommandsLogsBlacklistCategoryMissingPermission(
        description=LocalizedString('commands.logs.blacklistCategory.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistCategory.missingPermission.title'),
    )
    _n_commands_logs_blacklistCategory = CommandsLogsBlacklistCategory(
        alreadyBlacklisted=_n_commands_logs_blacklistCategory_alreadyBlacklisted,
        blacklisted=_n_commands_logs_blacklistCategory_blacklisted,
        missingChannel=_n_commands_logs_blacklistCategory_missingChannel,
        missingPermission=_n_commands_logs_blacklistCategory_missingPermission,
    )
    _n_commands_logs_blacklistChannel_alreadyBlacklisted = CommandsLogsBlacklistChannelAlreadyBlacklisted(
        description=LocalizedString('commands.logs.blacklistChannel.alreadyBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistChannel.alreadyBlacklisted.title'),
    )
    _n_commands_logs_blacklistChannel_blacklisted = CommandsLogsBlacklistChannelBlacklisted(
        description=LocalizedString('commands.logs.blacklistChannel.blacklisted.description'),
        title=LocalizedString('commands.logs.blacklistChannel.blacklisted.title'),
    )
    _n_commands_logs_blacklistChannel_missingPermission = CommandsLogsBlacklistChannelMissingPermission(
        description=LocalizedString('commands.logs.blacklistChannel.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistChannel.missingPermission.title'),
    )
    _n_commands_logs_blacklistChannel = CommandsLogsBlacklistChannel(
        alreadyBlacklisted=_n_commands_logs_blacklistChannel_alreadyBlacklisted,
        blacklisted=_n_commands_logs_blacklistChannel_blacklisted,
        missingPermission=_n_commands_logs_blacklistChannel_missingPermission,
    )
    _n_commands_logs_blacklistListCategory_addCategory = CommandsLogsBlacklistListCategoryAddCategory(
        placeholder=LocalizedString('commands.logs.blacklistListCategory.addCategory.placeholder'),
    )
    _n_commands_logs_blacklistListCategory_missingPermission = CommandsLogsBlacklistListCategoryMissingPermission(
        description=LocalizedString('commands.logs.blacklistListCategory.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistListCategory.missingPermission.title'),
    )
    _n_commands_logs_blacklistListCategory = CommandsLogsBlacklistListCategory(
        addCategory=_n_commands_logs_blacklistListCategory_addCategory,
        missingPermission=_n_commands_logs_blacklistListCategory_missingPermission,
        noBlacklistedCategories=LocalizedString('commands.logs.blacklistListCategory.noBlacklistedCategories'),
        title=LocalizedString('commands.logs.blacklistListCategory.title'),
    )
    _n_commands_logs_blacklistListChannel_addChannel = CommandsLogsBlacklistListChannelAddChannel(
        placeholder=LocalizedString('commands.logs.blacklistListChannel.addChannel.placeholder'),
    )
    _n_commands_logs_blacklistListChannel_missingPermission = CommandsLogsBlacklistListChannelMissingPermission(
        description=LocalizedString('commands.logs.blacklistListChannel.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistListChannel.missingPermission.title'),
    )
    _n_commands_logs_blacklistListChannel = CommandsLogsBlacklistListChannel(
        addChannel=_n_commands_logs_blacklistListChannel_addChannel,
        missingPermission=_n_commands_logs_blacklistListChannel_missingPermission,
        noBlacklistedChannels=LocalizedString('commands.logs.blacklistListChannel.noBlacklistedChannels'),
        title=LocalizedString('commands.logs.blacklistListChannel.title'),
    )
    _n_commands_logs_blacklistListRole_addRole = CommandsLogsBlacklistListRoleAddRole(
        placeholder=LocalizedString('commands.logs.blacklistListRole.addRole.placeholder'),
    )
    _n_commands_logs_blacklistListRole_missingPermission = CommandsLogsBlacklistListRoleMissingPermission(
        description=LocalizedString('commands.logs.blacklistListRole.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistListRole.missingPermission.title'),
    )
    _n_commands_logs_blacklistListRole = CommandsLogsBlacklistListRole(
        addRole=_n_commands_logs_blacklistListRole_addRole,
        missingPermission=_n_commands_logs_blacklistListRole_missingPermission,
        noBlacklistedRoles=LocalizedString('commands.logs.blacklistListRole.noBlacklistedRoles'),
        title=LocalizedString('commands.logs.blacklistListRole.title'),
    )
    _n_commands_logs_blacklistListUser_addUser = CommandsLogsBlacklistListUserAddUser(
        placeholder=LocalizedString('commands.logs.blacklistListUser.addUser.placeholder'),
    )
    _n_commands_logs_blacklistListUser_missingPermission = CommandsLogsBlacklistListUserMissingPermission(
        description=LocalizedString('commands.logs.blacklistListUser.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistListUser.missingPermission.title'),
    )
    _n_commands_logs_blacklistListUser = CommandsLogsBlacklistListUser(
        addUser=_n_commands_logs_blacklistListUser_addUser,
        missingPermission=_n_commands_logs_blacklistListUser_missingPermission,
        noBlacklistedUsers=LocalizedString('commands.logs.blacklistListUser.noBlacklistedUsers'),
        title=LocalizedString('commands.logs.blacklistListUser.title'),
    )
    _n_commands_logs_blacklistListVoiceChannel_addChannel = CommandsLogsBlacklistListVoiceChannelAddChannel(
        placeholder=LocalizedString('commands.logs.blacklistListVoiceChannel.addChannel.placeholder'),
    )
    _n_commands_logs_blacklistListVoiceChannel_missingPermission = CommandsLogsBlacklistListVoiceChannelMissingPermission(
        description=LocalizedString('commands.logs.blacklistListVoiceChannel.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistListVoiceChannel.missingPermission.title'),
    )
    _n_commands_logs_blacklistListVoiceChannel = CommandsLogsBlacklistListVoiceChannel(
        addChannel=_n_commands_logs_blacklistListVoiceChannel_addChannel,
        missingPermission=_n_commands_logs_blacklistListVoiceChannel_missingPermission,
        noBlacklistedChannels=LocalizedString('commands.logs.blacklistListVoiceChannel.noBlacklistedChannels'),
        title=LocalizedString('commands.logs.blacklistListVoiceChannel.title'),
    )
    _n_commands_logs_blacklistRemoveCategory_missingChannel = CommandsLogsBlacklistRemoveCategoryMissingChannel(
        description=LocalizedString('commands.logs.blacklistRemoveCategory.missingChannel.description'),
        title=LocalizedString('commands.logs.blacklistRemoveCategory.missingChannel.title'),
    )
    _n_commands_logs_blacklistRemoveCategory_missingPermission = CommandsLogsBlacklistRemoveCategoryMissingPermission(
        description=LocalizedString('commands.logs.blacklistRemoveCategory.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistRemoveCategory.missingPermission.title'),
    )
    _n_commands_logs_blacklistRemoveCategory_notBlacklisted = CommandsLogsBlacklistRemoveCategoryNotBlacklisted(
        description=LocalizedString('commands.logs.blacklistRemoveCategory.notBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistRemoveCategory.notBlacklisted.title'),
    )
    _n_commands_logs_blacklistRemoveCategory_success = CommandsLogsBlacklistRemoveCategorySuccess(
        description=LocalizedString('commands.logs.blacklistRemoveCategory.success.description'),
        title=LocalizedString('commands.logs.blacklistRemoveCategory.success.title'),
    )
    _n_commands_logs_blacklistRemoveCategory = CommandsLogsBlacklistRemoveCategory(
        missingChannel=_n_commands_logs_blacklistRemoveCategory_missingChannel,
        missingPermission=_n_commands_logs_blacklistRemoveCategory_missingPermission,
        notBlacklisted=_n_commands_logs_blacklistRemoveCategory_notBlacklisted,
        success=_n_commands_logs_blacklistRemoveCategory_success,
    )
    _n_commands_logs_blacklistRemoveChannel_missingPermission = CommandsLogsBlacklistRemoveChannelMissingPermission(
        description=LocalizedString('commands.logs.blacklistRemoveChannel.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistRemoveChannel.missingPermission.title'),
    )
    _n_commands_logs_blacklistRemoveChannel_notBlacklisted = CommandsLogsBlacklistRemoveChannelNotBlacklisted(
        description=LocalizedString('commands.logs.blacklistRemoveChannel.notBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistRemoveChannel.notBlacklisted.title'),
    )
    _n_commands_logs_blacklistRemoveChannel_success = CommandsLogsBlacklistRemoveChannelSuccess(
        description=LocalizedString('commands.logs.blacklistRemoveChannel.success.description'),
        title=LocalizedString('commands.logs.blacklistRemoveChannel.success.title'),
    )
    _n_commands_logs_blacklistRemoveChannel = CommandsLogsBlacklistRemoveChannel(
        missingPermission=_n_commands_logs_blacklistRemoveChannel_missingPermission,
        notBlacklisted=_n_commands_logs_blacklistRemoveChannel_notBlacklisted,
        success=_n_commands_logs_blacklistRemoveChannel_success,
    )
    _n_commands_logs_blacklistRemoveRole_missingPermission = CommandsLogsBlacklistRemoveRoleMissingPermission(
        description=LocalizedString('commands.logs.blacklistRemoveRole.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistRemoveRole.missingPermission.title'),
    )
    _n_commands_logs_blacklistRemoveRole_notBlacklisted = CommandsLogsBlacklistRemoveRoleNotBlacklisted(
        description=LocalizedString('commands.logs.blacklistRemoveRole.notBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistRemoveRole.notBlacklisted.title'),
    )
    _n_commands_logs_blacklistRemoveRole_success = CommandsLogsBlacklistRemoveRoleSuccess(
        description=LocalizedString('commands.logs.blacklistRemoveRole.success.description'),
        title=LocalizedString('commands.logs.blacklistRemoveRole.success.title'),
    )
    _n_commands_logs_blacklistRemoveRole = CommandsLogsBlacklistRemoveRole(
        missingPermission=_n_commands_logs_blacklistRemoveRole_missingPermission,
        notBlacklisted=_n_commands_logs_blacklistRemoveRole_notBlacklisted,
        success=_n_commands_logs_blacklistRemoveRole_success,
    )
    _n_commands_logs_blacklistRemoveUser_missingPermission = CommandsLogsBlacklistRemoveUserMissingPermission(
        description=LocalizedString('commands.logs.blacklistRemoveUser.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistRemoveUser.missingPermission.title'),
    )
    _n_commands_logs_blacklistRemoveUser_notBlacklisted = CommandsLogsBlacklistRemoveUserNotBlacklisted(
        description=LocalizedString('commands.logs.blacklistRemoveUser.notBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistRemoveUser.notBlacklisted.title'),
    )
    _n_commands_logs_blacklistRemoveUser_success = CommandsLogsBlacklistRemoveUserSuccess(
        description=LocalizedString('commands.logs.blacklistRemoveUser.success.description'),
        title=LocalizedString('commands.logs.blacklistRemoveUser.success.title'),
    )
    _n_commands_logs_blacklistRemoveUser = CommandsLogsBlacklistRemoveUser(
        missingPermission=_n_commands_logs_blacklistRemoveUser_missingPermission,
        notBlacklisted=_n_commands_logs_blacklistRemoveUser_notBlacklisted,
        success=_n_commands_logs_blacklistRemoveUser_success,
    )
    _n_commands_logs_blacklistRemoveVoiceChannel_missingChannel = CommandsLogsBlacklistRemoveVoiceChannelMissingChannel(
        description=LocalizedString('commands.logs.blacklistRemoveVoiceChannel.missingChannel.description'),
        title=LocalizedString('commands.logs.blacklistRemoveVoiceChannel.missingChannel.title'),
    )
    _n_commands_logs_blacklistRemoveVoiceChannel_missingPermission = CommandsLogsBlacklistRemoveVoiceChannelMissingPermission(
        description=LocalizedString('commands.logs.blacklistRemoveVoiceChannel.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistRemoveVoiceChannel.missingPermission.title'),
    )
    _n_commands_logs_blacklistRemoveVoiceChannel_notBlacklisted = CommandsLogsBlacklistRemoveVoiceChannelNotBlacklisted(
        description=LocalizedString('commands.logs.blacklistRemoveVoiceChannel.notBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistRemoveVoiceChannel.notBlacklisted.title'),
    )
    _n_commands_logs_blacklistRemoveVoiceChannel_success = CommandsLogsBlacklistRemoveVoiceChannelSuccess(
        description=LocalizedString('commands.logs.blacklistRemoveVoiceChannel.success.description'),
        title=LocalizedString('commands.logs.blacklistRemoveVoiceChannel.success.title'),
    )
    _n_commands_logs_blacklistRemoveVoiceChannel = CommandsLogsBlacklistRemoveVoiceChannel(
        missingChannel=_n_commands_logs_blacklistRemoveVoiceChannel_missingChannel,
        missingPermission=_n_commands_logs_blacklistRemoveVoiceChannel_missingPermission,
        notBlacklisted=_n_commands_logs_blacklistRemoveVoiceChannel_notBlacklisted,
        success=_n_commands_logs_blacklistRemoveVoiceChannel_success,
    )
    _n_commands_logs_blacklistRole_alreadyBlacklisted = CommandsLogsBlacklistRoleAlreadyBlacklisted(
        description=LocalizedString('commands.logs.blacklistRole.alreadyBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistRole.alreadyBlacklisted.title'),
    )
    _n_commands_logs_blacklistRole_blacklisted = CommandsLogsBlacklistRoleBlacklisted(
        description=LocalizedString('commands.logs.blacklistRole.blacklisted.description'),
        title=LocalizedString('commands.logs.blacklistRole.blacklisted.title'),
    )
    _n_commands_logs_blacklistRole_missingPermission = CommandsLogsBlacklistRoleMissingPermission(
        description=LocalizedString('commands.logs.blacklistRole.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistRole.missingPermission.title'),
    )
    _n_commands_logs_blacklistRole = CommandsLogsBlacklistRole(
        alreadyBlacklisted=_n_commands_logs_blacklistRole_alreadyBlacklisted,
        blacklisted=_n_commands_logs_blacklistRole_blacklisted,
        missingPermission=_n_commands_logs_blacklistRole_missingPermission,
    )
    _n_commands_logs_blacklistUser_alreadyBlacklisted = CommandsLogsBlacklistUserAlreadyBlacklisted(
        description=LocalizedString('commands.logs.blacklistUser.alreadyBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistUser.alreadyBlacklisted.title'),
    )
    _n_commands_logs_blacklistUser_blacklisted = CommandsLogsBlacklistUserBlacklisted(
        description=LocalizedString('commands.logs.blacklistUser.blacklisted.description'),
        title=LocalizedString('commands.logs.blacklistUser.blacklisted.title'),
    )
    _n_commands_logs_blacklistUser_missingPermission = CommandsLogsBlacklistUserMissingPermission(
        description=LocalizedString('commands.logs.blacklistUser.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistUser.missingPermission.title'),
    )
    _n_commands_logs_blacklistUser = CommandsLogsBlacklistUser(
        alreadyBlacklisted=_n_commands_logs_blacklistUser_alreadyBlacklisted,
        blacklisted=_n_commands_logs_blacklistUser_blacklisted,
        missingPermission=_n_commands_logs_blacklistUser_missingPermission,
    )
    _n_commands_logs_blacklistVoiceChannel_alreadyBlacklisted = CommandsLogsBlacklistVoiceChannelAlreadyBlacklisted(
        description=LocalizedString('commands.logs.blacklistVoiceChannel.alreadyBlacklisted.description'),
        title=LocalizedString('commands.logs.blacklistVoiceChannel.alreadyBlacklisted.title'),
    )
    _n_commands_logs_blacklistVoiceChannel_blacklisted = CommandsLogsBlacklistVoiceChannelBlacklisted(
        description=LocalizedString('commands.logs.blacklistVoiceChannel.blacklisted.description'),
        title=LocalizedString('commands.logs.blacklistVoiceChannel.blacklisted.title'),
    )
    _n_commands_logs_blacklistVoiceChannel_missingChannel = CommandsLogsBlacklistVoiceChannelMissingChannel(
        description=LocalizedString('commands.logs.blacklistVoiceChannel.missingChannel.description'),
        title=LocalizedString('commands.logs.blacklistVoiceChannel.missingChannel.title'),
    )
    _n_commands_logs_blacklistVoiceChannel_missingPermission = CommandsLogsBlacklistVoiceChannelMissingPermission(
        description=LocalizedString('commands.logs.blacklistVoiceChannel.missingPermission.description'),
        title=LocalizedString('commands.logs.blacklistVoiceChannel.missingPermission.title'),
    )
    _n_commands_logs_blacklistVoiceChannel = CommandsLogsBlacklistVoiceChannel(
        alreadyBlacklisted=_n_commands_logs_blacklistVoiceChannel_alreadyBlacklisted,
        blacklisted=_n_commands_logs_blacklistVoiceChannel_blacklisted,
        missingChannel=_n_commands_logs_blacklistVoiceChannel_missingChannel,
        missingPermission=_n_commands_logs_blacklistVoiceChannel_missingPermission,
    )
    _n_commands_logs_configureLogs_configurationEmbed = CommandsLogsConfigureLogsConfigurationEmbed(
        activate=LocalizedString('commands.logs.configureLogs.configurationEmbed.activate'),
        activated=LocalizedString('commands.logs.configureLogs.configurationEmbed.activated'),
        automodAction=LocalizedString('commands.logs.configureLogs.configurationEmbed.automodAction'),
        automodRuleCreate=LocalizedString('commands.logs.configureLogs.configurationEmbed.automodRuleCreate'),
        automodRuleDelete=LocalizedString('commands.logs.configureLogs.configurationEmbed.automodRuleDelete'),
        automodRuleUpdate=LocalizedString('commands.logs.configureLogs.configurationEmbed.automodRuleUpdate'),
        deactivate=LocalizedString('commands.logs.configureLogs.configurationEmbed.deactivate'),
        deactivated=LocalizedString('commands.logs.configureLogs.configurationEmbed.deactivated'),
        guildChannelCreate=LocalizedString('commands.logs.configureLogs.configurationEmbed.guildChannelCreate'),
        guildChannelDelete=LocalizedString('commands.logs.configureLogs.configurationEmbed.guildChannelDelete'),
        guildChannelUpdate=LocalizedString('commands.logs.configureLogs.configurationEmbed.guildChannelUpdate'),
        guildRoleCreate=LocalizedString('commands.logs.configureLogs.configurationEmbed.guildRoleCreate'),
        guildRoleDelete=LocalizedString('commands.logs.configureLogs.configurationEmbed.guildRoleDelete'),
        guildRoleUpdate=LocalizedString('commands.logs.configureLogs.configurationEmbed.guildRoleUpdate'),
        guildUpdate=LocalizedString('commands.logs.configureLogs.configurationEmbed.guildUpdate'),
        inviteCreate=LocalizedString('commands.logs.configureLogs.configurationEmbed.inviteCreate'),
        inviteDelete=LocalizedString('commands.logs.configureLogs.configurationEmbed.inviteDelete'),
        memberBan=LocalizedString('commands.logs.configureLogs.configurationEmbed.memberBan'),
        memberJoin=LocalizedString('commands.logs.configureLogs.configurationEmbed.memberJoin'),
        memberLeave=LocalizedString('commands.logs.configureLogs.configurationEmbed.memberLeave'),
        memberUnban=LocalizedString('commands.logs.configureLogs.configurationEmbed.memberUnban'),
        memberUpdate=LocalizedString('commands.logs.configureLogs.configurationEmbed.memberUpdate'),
        messageDelete=LocalizedString('commands.logs.configureLogs.configurationEmbed.messageDelete'),
        messageEdit=LocalizedString('commands.logs.configureLogs.configurationEmbed.messageEdit'),
        presenceUpdate=LocalizedString('commands.logs.configureLogs.configurationEmbed.presenceUpdate'),
        reactionAdd=LocalizedString('commands.logs.configureLogs.configurationEmbed.reactionAdd'),
        reactionRemove=LocalizedString('commands.logs.configureLogs.configurationEmbed.reactionRemove'),
        title=LocalizedString('commands.logs.configureLogs.configurationEmbed.title'),
        userUpdate=LocalizedString('commands.logs.configureLogs.configurationEmbed.userUpdate'),
    )
    _n_commands_logs_configureLogs_configuration_embed = CommandsLogsConfigureLogsConfiguration_embed(
        activate=LocalizedString('commands.logs.configureLogs.configuration_embed.activate'),
        activated=LocalizedString('commands.logs.configureLogs.configuration_embed.activated'),
        automodAction=LocalizedString('commands.logs.configureLogs.configuration_embed.automodAction'),
        automodRuleCreate=LocalizedString('commands.logs.configureLogs.configuration_embed.automodRuleCreate'),
        automodRuleDelete=LocalizedString('commands.logs.configureLogs.configuration_embed.automodRuleDelete'),
        automodRuleUpdate=LocalizedString('commands.logs.configureLogs.configuration_embed.automodRuleUpdate'),
        deactivate=LocalizedString('commands.logs.configureLogs.configuration_embed.deactivate'),
        deactivated=LocalizedString('commands.logs.configureLogs.configuration_embed.deactivated'),
        guildRoleCreate=LocalizedString('commands.logs.configureLogs.configuration_embed.guildRoleCreate'),
        guildRoleDelete=LocalizedString('commands.logs.configureLogs.configuration_embed.guildRoleDelete'),
        guildRoleUpdate=LocalizedString('commands.logs.configureLogs.configuration_embed.guildRoleUpdate'),
        guildUpdate=LocalizedString('commands.logs.configureLogs.configuration_embed.guildUpdate'),
        guild_channelCreate=LocalizedString('commands.logs.configureLogs.configuration_embed.guild_channelCreate'),
        guild_channelDelete=LocalizedString('commands.logs.configureLogs.configuration_embed.guild_channelDelete'),
        guild_channelUpdate=LocalizedString('commands.logs.configureLogs.configuration_embed.guild_channelUpdate'),
        inviteCreate=LocalizedString('commands.logs.configureLogs.configuration_embed.inviteCreate'),
        inviteDelete=LocalizedString('commands.logs.configureLogs.configuration_embed.inviteDelete'),
        memberBan=LocalizedString('commands.logs.configureLogs.configuration_embed.memberBan'),
        memberJoin=LocalizedString('commands.logs.configureLogs.configuration_embed.memberJoin'),
        memberLeave=LocalizedString('commands.logs.configureLogs.configuration_embed.memberLeave'),
        memberUnban=LocalizedString('commands.logs.configureLogs.configuration_embed.memberUnban'),
        memberUpdate=LocalizedString('commands.logs.configureLogs.configuration_embed.memberUpdate'),
        messageDelete=LocalizedString('commands.logs.configureLogs.configuration_embed.messageDelete'),
        messageEdit=LocalizedString('commands.logs.configureLogs.configuration_embed.messageEdit'),
        presenceUpdate=LocalizedString('commands.logs.configureLogs.configuration_embed.presenceUpdate'),
        reactionAdd=LocalizedString('commands.logs.configureLogs.configuration_embed.reactionAdd'),
        reactionRemove=LocalizedString('commands.logs.configureLogs.configuration_embed.reactionRemove'),
        userUpdate=LocalizedString('commands.logs.configureLogs.configuration_embed.userUpdate'),
    )
    _n_commands_logs_configureLogs_noLogEnabled = CommandsLogsConfigureLogsNoLogEnabled(
        description=LocalizedString('commands.logs.configureLogs.noLogEnabled.description'),
        title=LocalizedString('commands.logs.configureLogs.noLogEnabled.title'),
    )
    _n_commands_logs_configureLogs = CommandsLogsConfigureLogs(
        configurationEmbed=_n_commands_logs_configureLogs_configurationEmbed,
        configuration_embed=_n_commands_logs_configureLogs_configuration_embed,
        noLogEnabled=_n_commands_logs_configureLogs_noLogEnabled,
        title=LocalizedString('commands.logs.configureLogs.title'),
    )
    _n_commands_logs_removeLogChannel_missingPermission = CommandsLogsRemoveLogChannelMissingPermission(
        description=LocalizedString('commands.logs.removeLogChannel.missingPermission.description'),
        title=LocalizedString('commands.logs.removeLogChannel.missingPermission.title'),
    )
    _n_commands_logs_removeLogChannel_notSet = CommandsLogsRemoveLogChannelNotSet(
        description=LocalizedString('commands.logs.removeLogChannel.notSet.description'),
        title=LocalizedString('commands.logs.removeLogChannel.notSet.title'),
    )
    _n_commands_logs_removeLogChannel_success = CommandsLogsRemoveLogChannelSuccess(
        description=LocalizedString('commands.logs.removeLogChannel.success.description'),
        title=LocalizedString('commands.logs.removeLogChannel.success.title'),
    )
    _n_commands_logs_removeLogChannel = CommandsLogsRemoveLogChannel(
        missingPermission=_n_commands_logs_removeLogChannel_missingPermission,
        notSet=_n_commands_logs_removeLogChannel_notSet,
        success=_n_commands_logs_removeLogChannel_success,
    )
    _n_commands_logs_setLogChannel_alreadySet = CommandsLogsSetLogChannelAlreadySet(
        description=LocalizedString('commands.logs.setLogChannel.alreadySet.description'),
        title=LocalizedString('commands.logs.setLogChannel.alreadySet.title'),
    )
    _n_commands_logs_setLogChannel_botMissingPermission = CommandsLogsSetLogChannelBotMissingPermission(
        description=LocalizedString('commands.logs.setLogChannel.botMissingPermission.description'),
        title=LocalizedString('commands.logs.setLogChannel.botMissingPermission.title'),
    )
    _n_commands_logs_setLogChannel_missingPermission = CommandsLogsSetLogChannelMissingPermission(
        description=LocalizedString('commands.logs.setLogChannel.missingPermission.description'),
        title=LocalizedString('commands.logs.setLogChannel.missingPermission.title'),
    )
    _n_commands_logs_setLogChannel_success = CommandsLogsSetLogChannelSuccess(
        description=LocalizedString('commands.logs.setLogChannel.success.description'),
        title=LocalizedString('commands.logs.setLogChannel.success.title'),
    )
    _n_commands_logs_setLogChannel = CommandsLogsSetLogChannel(
        alreadySet=_n_commands_logs_setLogChannel_alreadySet,
        botMissingPermission=_n_commands_logs_setLogChannel_botMissingPermission,
        missingPermission=_n_commands_logs_setLogChannel_missingPermission,
        success=_n_commands_logs_setLogChannel_success,
    )
    _n_commands_logs = CommandsLogs(
        _text=LocalizedString('commands.logs'),
        blacklist=_n_commands_logs_blacklist,
        blacklistCategory=_n_commands_logs_blacklistCategory,
        blacklistChannel=_n_commands_logs_blacklistChannel,
        blacklistListCategory=_n_commands_logs_blacklistListCategory,
        blacklistListChannel=_n_commands_logs_blacklistListChannel,
        blacklistListRole=_n_commands_logs_blacklistListRole,
        blacklistListUser=_n_commands_logs_blacklistListUser,
        blacklistListVoiceChannel=_n_commands_logs_blacklistListVoiceChannel,
        blacklistRemoveCategory=_n_commands_logs_blacklistRemoveCategory,
        blacklistRemoveChannel=_n_commands_logs_blacklistRemoveChannel,
        blacklistRemoveRole=_n_commands_logs_blacklistRemoveRole,
        blacklistRemoveUser=_n_commands_logs_blacklistRemoveUser,
        blacklistRemoveVoiceChannel=_n_commands_logs_blacklistRemoveVoiceChannel,
        blacklistRole=_n_commands_logs_blacklistRole,
        blacklistUser=_n_commands_logs_blacklistUser,
        blacklistVoiceChannel=_n_commands_logs_blacklistVoiceChannel,
        configureLogs=_n_commands_logs_configureLogs,
        removeLogChannel=_n_commands_logs_removeLogChannel,
        setLogChannel=_n_commands_logs_setLogChannel,
    )
    _n_commands_math_calc_error = CommandsMathCalcError(
        description=LocalizedString('commands.math.calc.error.description'),
        title=LocalizedString('commands.math.calc.error.title'),
    )
    _n_commands_math_calc_success = CommandsMathCalcSuccess(
        description=LocalizedString('commands.math.calc.success.description'),
        title=LocalizedString('commands.math.calc.success.title'),
    )
    _n_commands_math_calc = CommandsMathCalc(
        error=_n_commands_math_calc_error,
        success=_n_commands_math_calc_success,
    )
    _n_commands_math_calculator = CommandsMathCalculator(
        command_description=LocalizedString('commands.math.calculator.command_description'),
        command_name=LocalizedString('commands.math.calculator.command_name'),
        equation=LocalizedString('commands.math.calculator.equation'),
        error=LocalizedString('commands.math.calculator.error'),
        history=LocalizedString('commands.math.calculator.history'),
        invalid_assignment=LocalizedString('commands.math.calculator.invalid_assignment'),
        result=LocalizedString('commands.math.calculator.result'),
        title=LocalizedString('commands.math.calculator.title'),
        unauthorizedUser=LocalizedString('commands.math.calculator.unauthorizedUser'),
        variables=LocalizedString('commands.math.calculator.variables'),
    )
    _n_commands_math_faculty_error = CommandsMathFacultyError(
        invalid_input=LocalizedString('commands.math.faculty.error.invalid_input'),
        invalid_number=LocalizedString('commands.math.faculty.error.invalid_number'),
        invalid_number2=LocalizedString('commands.math.faculty.error.invalid_number2'),
        title=LocalizedString('commands.math.faculty.error.title'),
    )
    _n_commands_math_faculty_success = CommandsMathFacultySuccess(
        description=LocalizedString('commands.math.faculty.success.description'),
        title=LocalizedString('commands.math.faculty.success.title'),
    )
    _n_commands_math_faculty = CommandsMathFaculty(
        error=_n_commands_math_faculty_error,
        success=_n_commands_math_faculty_success,
    )
    _n_commands_math_num2word_locales_en = CommandsMathNum2wordLocalesEn(
        GB=LocalizedString('commands.math.num2word.locales.en.GB'),
        IN=LocalizedString('commands.math.num2word.locales.en.IN'),
        NG=LocalizedString('commands.math.num2word.locales.en.NG'),
        _text=LocalizedString('commands.math.num2word.locales.en'),
    )
    _n_commands_math_num2word_locales_es = CommandsMathNum2wordLocalesEs(
        CO=LocalizedString('commands.math.num2word.locales.es.CO'),
        CR=LocalizedString('commands.math.num2word.locales.es.CR'),
        GT=LocalizedString('commands.math.num2word.locales.es.GT'),
        VE=LocalizedString('commands.math.num2word.locales.es.VE'),
        _text=LocalizedString('commands.math.num2word.locales.es'),
    )
    _n_commands_math_num2word_locales_fr = CommandsMathNum2wordLocalesFr(
        BE=LocalizedString('commands.math.num2word.locales.fr.BE'),
        CH=LocalizedString('commands.math.num2word.locales.fr.CH'),
        DZ=LocalizedString('commands.math.num2word.locales.fr.DZ'),
        _text=LocalizedString('commands.math.num2word.locales.fr'),
    )
    _n_commands_math_num2word_locales_pt = CommandsMathNum2wordLocalesPt(
        BR=LocalizedString('commands.math.num2word.locales.pt.BR'),
        _text=LocalizedString('commands.math.num2word.locales.pt'),
    )
    _n_commands_math_num2word_locales = CommandsMathNum2wordLocales(
        am=LocalizedString('commands.math.num2word.locales.am'),
        ar=LocalizedString('commands.math.num2word.locales.ar'),
        az=LocalizedString('commands.math.num2word.locales.az'),
        by=LocalizedString('commands.math.num2word.locales.by'),
        ce=LocalizedString('commands.math.num2word.locales.ce'),
        cy=LocalizedString('commands.math.num2word.locales.cy'),
        cz=LocalizedString('commands.math.num2word.locales.cz'),
        de=LocalizedString('commands.math.num2word.locales.de'),
        dk=LocalizedString('commands.math.num2word.locales.dk'),
        en=_n_commands_math_num2word_locales_en,
        es=_n_commands_math_num2word_locales_es,
        eu=LocalizedString('commands.math.num2word.locales.eu'),
        fa=LocalizedString('commands.math.num2word.locales.fa'),
        fi=LocalizedString('commands.math.num2word.locales.fi'),
        fr=_n_commands_math_num2word_locales_fr,
        he=LocalizedString('commands.math.num2word.locales.he'),
        hu=LocalizedString('commands.math.num2word.locales.hu'),
        id=LocalizedString('commands.math.num2word.locales.id'),
        is_=LocalizedString('commands.math.num2word.locales.is'),
        it=LocalizedString('commands.math.num2word.locales.it'),
        ja=LocalizedString('commands.math.num2word.locales.ja'),
        kn=LocalizedString('commands.math.num2word.locales.kn'),
        ko=LocalizedString('commands.math.num2word.locales.ko'),
        kz=LocalizedString('commands.math.num2word.locales.kz'),
        lt=LocalizedString('commands.math.num2word.locales.lt'),
        lv=LocalizedString('commands.math.num2word.locales.lv'),
        nl=LocalizedString('commands.math.num2word.locales.nl'),
        no=LocalizedString('commands.math.num2word.locales.no'),
        pl=LocalizedString('commands.math.num2word.locales.pl'),
        pt=_n_commands_math_num2word_locales_pt,
        ro=LocalizedString('commands.math.num2word.locales.ro'),
        ru=LocalizedString('commands.math.num2word.locales.ru'),
        sl=LocalizedString('commands.math.num2word.locales.sl'),
        sr=LocalizedString('commands.math.num2word.locales.sr'),
        sv=LocalizedString('commands.math.num2word.locales.sv'),
        te=LocalizedString('commands.math.num2word.locales.te'),
        tg=LocalizedString('commands.math.num2word.locales.tg'),
        th=LocalizedString('commands.math.num2word.locales.th'),
        tr=LocalizedString('commands.math.num2word.locales.tr'),
        uk=LocalizedString('commands.math.num2word.locales.uk'),
        vi=LocalizedString('commands.math.num2word.locales.vi'),
    )
    _n_commands_math_num2word = CommandsMathNum2word(
        description=LocalizedString('commands.math.num2word.description'),
        locales=_n_commands_math_num2word_locales,
        title=LocalizedString('commands.math.num2word.title'),
    )
    _n_commands_math_plot_function = CommandsMathPlot_function(
        error=LocalizedString('commands.math.plot_function.error'),
        no_functions_to_rename=LocalizedString('commands.math.plot_function.no_functions_to_rename'),
        not_clickable=LocalizedString('commands.math.plot_function.not_clickable'),
        unexpected_error=LocalizedString('commands.math.plot_function.unexpected_error'),
    )
    _n_commands_math_plotfunction_buttons = CommandsMathPlotfunctionButtons(
        add_function=LocalizedString('commands.math.plotfunction.buttons.add_function'),
        change_style=LocalizedString('commands.math.plotfunction.buttons.change_style'),
        change_x_label=LocalizedString('commands.math.plotfunction.buttons.change_x_label'),
        change_y_label=LocalizedString('commands.math.plotfunction.buttons.change_y_label'),
        derive=LocalizedString('commands.math.plotfunction.buttons.derive'),
        integrate=LocalizedString('commands.math.plotfunction.buttons.integrate'),
        move_down=LocalizedString('commands.math.plotfunction.buttons.move_down'),
        move_left=LocalizedString('commands.math.plotfunction.buttons.move_left'),
        move_right=LocalizedString('commands.math.plotfunction.buttons.move_right'),
        move_up=LocalizedString('commands.math.plotfunction.buttons.move_up'),
        rename_function=LocalizedString('commands.math.plotfunction.buttons.rename_function'),
        rename_plot=LocalizedString('commands.math.plotfunction.buttons.rename_plot'),
        zoom_in=LocalizedString('commands.math.plotfunction.buttons.zoom_in'),
        zoom_out=LocalizedString('commands.math.plotfunction.buttons.zoom_out'),
    )
    _n_commands_math_plotfunction_error = CommandsMathPlotfunctionError(
        description=LocalizedString('commands.math.plotfunction.error.description'),
        title=LocalizedString('commands.math.plotfunction.error.title'),
    )
    _n_commands_math_plotfunction_messages = CommandsMathPlotfunctionMessages(
        error_occurred=LocalizedString('commands.math.plotfunction.messages.error_occurred'),
        function_added=LocalizedString('commands.math.plotfunction.messages.function_added'),
        function_derived=LocalizedString('commands.math.plotfunction.messages.function_derived'),
        function_integrated=LocalizedString('commands.math.plotfunction.messages.function_integrated'),
        function_renamed=LocalizedString('commands.math.plotfunction.messages.function_renamed'),
        no_permission=LocalizedString('commands.math.plotfunction.messages.no_permission'),
        plot_updated=LocalizedString('commands.math.plotfunction.messages.plot_updated'),
        style_changed=LocalizedString('commands.math.plotfunction.messages.style_changed'),
        title_changed=LocalizedString('commands.math.plotfunction.messages.title_changed'),
        x_label_changed=LocalizedString('commands.math.plotfunction.messages.x_label_changed'),
        y_label_changed=LocalizedString('commands.math.plotfunction.messages.y_label_changed'),
    )
    _n_commands_math_plotfunction_modals_add_function = CommandsMathPlotfunctionModalsAdd_function(
        function_expression=LocalizedString('commands.math.plotfunction.modals.add_function.function_expression'),
        function_expression_placeholder=LocalizedString('commands.math.plotfunction.modals.add_function.function_expression_placeholder'),
        function_name=LocalizedString('commands.math.plotfunction.modals.add_function.function_name'),
        function_name_placeholder=LocalizedString('commands.math.plotfunction.modals.add_function.function_name_placeholder'),
        title=LocalizedString('commands.math.plotfunction.modals.add_function.title'),
    )
    _n_commands_math_plotfunction_modals_change_title = CommandsMathPlotfunctionModalsChange_title(
        new_title=LocalizedString('commands.math.plotfunction.modals.change_title.new_title'),
        new_title_placeholder=LocalizedString('commands.math.plotfunction.modals.change_title.new_title_placeholder'),
        title=LocalizedString('commands.math.plotfunction.modals.change_title.title'),
    )
    _n_commands_math_plotfunction_modals_change_x_label = CommandsMathPlotfunctionModalsChange_x_label(
        new_label=LocalizedString('commands.math.plotfunction.modals.change_x_label.new_label'),
        new_label_placeholder=LocalizedString('commands.math.plotfunction.modals.change_x_label.new_label_placeholder'),
        title=LocalizedString('commands.math.plotfunction.modals.change_x_label.title'),
    )
    _n_commands_math_plotfunction_modals_change_y_label = CommandsMathPlotfunctionModalsChange_y_label(
        new_label=LocalizedString('commands.math.plotfunction.modals.change_y_label.new_label'),
        new_label_placeholder=LocalizedString('commands.math.plotfunction.modals.change_y_label.new_label_placeholder'),
        title=LocalizedString('commands.math.plotfunction.modals.change_y_label.title'),
    )
    _n_commands_math_plotfunction_modals_rename_function = CommandsMathPlotfunctionModalsRename_function(
        new_name=LocalizedString('commands.math.plotfunction.modals.rename_function.new_name'),
        new_name_placeholder=LocalizedString('commands.math.plotfunction.modals.rename_function.new_name_placeholder'),
        title=LocalizedString('commands.math.plotfunction.modals.rename_function.title'),
    )
    _n_commands_math_plotfunction_modals = CommandsMathPlotfunctionModals(
        add_function=_n_commands_math_plotfunction_modals_add_function,
        change_title=_n_commands_math_plotfunction_modals_change_title,
        change_x_label=_n_commands_math_plotfunction_modals_change_x_label,
        change_y_label=_n_commands_math_plotfunction_modals_change_y_label,
        rename_function=_n_commands_math_plotfunction_modals_rename_function,
    )
    _n_commands_math_plotfunction_select_menus_derive = CommandsMathPlotfunctionSelect_menusDerive(
        placeholder=LocalizedString('commands.math.plotfunction.select_menus.derive.placeholder'),
    )
    _n_commands_math_plotfunction_select_menus_integrate = CommandsMathPlotfunctionSelect_menusIntegrate(
        placeholder=LocalizedString('commands.math.plotfunction.select_menus.integrate.placeholder'),
    )
    _n_commands_math_plotfunction_select_menus_rename_function = CommandsMathPlotfunctionSelect_menusRename_function(
        placeholder=LocalizedString('commands.math.plotfunction.select_menus.rename_function.placeholder'),
    )
    _n_commands_math_plotfunction_select_menus_style = CommandsMathPlotfunctionSelect_menusStyle(
        placeholder=LocalizedString('commands.math.plotfunction.select_menus.style.placeholder'),
    )
    _n_commands_math_plotfunction_select_menus = CommandsMathPlotfunctionSelect_menus(
        derive=_n_commands_math_plotfunction_select_menus_derive,
        integrate=_n_commands_math_plotfunction_select_menus_integrate,
        rename_function=_n_commands_math_plotfunction_select_menus_rename_function,
        style=_n_commands_math_plotfunction_select_menus_style,
    )
    _n_commands_math_plotfunction = CommandsMathPlotfunction(
        buttons=_n_commands_math_plotfunction_buttons,
        default_title=LocalizedString('commands.math.plotfunction.default_title'),
        default_x_label=LocalizedString('commands.math.plotfunction.default_x_label'),
        default_y_label=LocalizedString('commands.math.plotfunction.default_y_label'),
        description=LocalizedString('commands.math.plotfunction.description'),
        error=_n_commands_math_plotfunction_error,
        extrema=LocalizedString('commands.math.plotfunction.extrema'),
        extremum=LocalizedString('commands.math.plotfunction.extremum'),
        inflection=LocalizedString('commands.math.plotfunction.inflection'),
        inflection_points=LocalizedString('commands.math.plotfunction.inflection_points'),
        messages=_n_commands_math_plotfunction_messages,
        modals=_n_commands_math_plotfunction_modals,
        no_functions_to_rename=LocalizedString('commands.math.plotfunction.no_functions_to_rename'),
        not_clickable=LocalizedString('commands.math.plotfunction.not_clickable'),
        plot_title=LocalizedString('commands.math.plotfunction.plot_title'),
        select_menus=_n_commands_math_plotfunction_select_menus,
        unexpected_error=LocalizedString('commands.math.plotfunction.unexpected_error'),
        x_axis=LocalizedString('commands.math.plotfunction.x_axis'),
        y_axis=LocalizedString('commands.math.plotfunction.y_axis'),
        zero=LocalizedString('commands.math.plotfunction.zero'),
        zeros=LocalizedString('commands.math.plotfunction.zeros'),
    )
    _n_commands_math_randomnumber_error = CommandsMathRandomnumberError(
        invalid_amount=LocalizedString('commands.math.randomnumber.error.invalid_amount'),
        invalid_input=LocalizedString('commands.math.randomnumber.error.invalid_input'),
        invalid_range=LocalizedString('commands.math.randomnumber.error.invalid_range'),
        title=LocalizedString('commands.math.randomnumber.error.title'),
    )
    _n_commands_math_randomnumber_success = CommandsMathRandomnumberSuccess(
        description=LocalizedString('commands.math.randomnumber.success.description'),
        title=LocalizedString('commands.math.randomnumber.success.title'),
    )
    _n_commands_math_randomnumber = CommandsMathRandomnumber(
        error=_n_commands_math_randomnumber_error,
        not_truly_random=LocalizedString('commands.math.randomnumber.not_truly_random'),
        success=_n_commands_math_randomnumber_success,
    )
    _n_commands_math = CommandsMath(
        calc=_n_commands_math_calc,
        calculator=_n_commands_math_calculator,
        faculty=_n_commands_math_faculty,
        num2word=_n_commands_math_num2word,
        plot_function=_n_commands_math_plot_function,
        plotfunction=_n_commands_math_plotfunction,
        randomnumber=_n_commands_math_randomnumber,
    )
    _n_commands_utility_afk_already_afk = CommandsUtilityAfkAlready_afk(
        description=LocalizedString('commands.utility.afk.already_afk.description'),
        title=LocalizedString('commands.utility.afk.already_afk.title'),
    )
    _n_commands_utility_afk_mentions = CommandsUtilityAfkMentions(
        description=LocalizedString('commands.utility.afk.mentions.description'),
        title=LocalizedString('commands.utility.afk.mentions.title'),
    )
    _n_commands_utility_afk_mentions_one = CommandsUtilityAfkMentions_one(
        description=LocalizedString('commands.utility.afk.mentions_one.description'),
        title=LocalizedString('commands.utility.afk.mentions_one.title'),
    )
    _n_commands_utility_afk_opted_out = CommandsUtilityAfkOpted_out(
        description=LocalizedString('commands.utility.afk.opted_out.description'),
        title=LocalizedString('commands.utility.afk.opted_out.title'),
    )
    _n_commands_utility_afk_removed = CommandsUtilityAfkRemoved(
        description=LocalizedString('commands.utility.afk.removed.description'),
        title=LocalizedString('commands.utility.afk.removed.title'),
    )
    _n_commands_utility_afk_removed_no_messages = CommandsUtilityAfkRemoved_no_messages(
        description=LocalizedString('commands.utility.afk.removed_no_messages.description'),
        title=LocalizedString('commands.utility.afk.removed_no_messages.title'),
    )
    _n_commands_utility_afk_success = CommandsUtilityAfkSuccess(
        description=LocalizedString('commands.utility.afk.success.description'),
        title=LocalizedString('commands.utility.afk.success.title'),
    )
    _n_commands_utility_afk = CommandsUtilityAfk(
        already_afk=_n_commands_utility_afk_already_afk,
        mentions=_n_commands_utility_afk_mentions,
        mentions_one=_n_commands_utility_afk_mentions_one,
        opted_out=_n_commands_utility_afk_opted_out,
        removed=_n_commands_utility_afk_removed,
        removed_no_messages=_n_commands_utility_afk_removed_no_messages,
        success=_n_commands_utility_afk_success,
    )
    _n_commands_utility_autopublish_error_is_already = CommandsUtilityAutopublishErrorIs_already(
        description=LocalizedString('commands.utility.autopublish.error.is_already.description'),
        title=LocalizedString('commands.utility.autopublish.error.is_already.title'),
    )
    _n_commands_utility_autopublish_error_is_not = CommandsUtilityAutopublishErrorIs_not(
        description=LocalizedString('commands.utility.autopublish.error.is_not.description'),
        title=LocalizedString('commands.utility.autopublish.error.is_not.title'),
    )
    _n_commands_utility_autopublish_error_no_permission = CommandsUtilityAutopublishErrorNo_permission(
        description=LocalizedString('commands.utility.autopublish.error.no_permission.description'),
        title=LocalizedString('commands.utility.autopublish.error.no_permission.title'),
    )
    _n_commands_utility_autopublish_error_not_news_channel = CommandsUtilityAutopublishErrorNot_news_channel(
        description=LocalizedString('commands.utility.autopublish.error.not_news_channel.description'),
        title=LocalizedString('commands.utility.autopublish.error.not_news_channel.title'),
    )
    _n_commands_utility_autopublish_error = CommandsUtilityAutopublishError(
        is_already=_n_commands_utility_autopublish_error_is_already,
        is_not=_n_commands_utility_autopublish_error_is_not,
        no_permission=_n_commands_utility_autopublish_error_no_permission,
        not_news_channel=_n_commands_utility_autopublish_error_not_news_channel,
    )
    _n_commands_utility_autopublish_remove_success = CommandsUtilityAutopublishRemove_success(
        description=LocalizedString('commands.utility.autopublish.remove_success.description'),
        title=LocalizedString('commands.utility.autopublish.remove_success.title'),
    )
    _n_commands_utility_autopublish_success = CommandsUtilityAutopublishSuccess(
        description=LocalizedString('commands.utility.autopublish.success.description'),
        title=LocalizedString('commands.utility.autopublish.success.title'),
    )
    _n_commands_utility_autopublish = CommandsUtilityAutopublish(
        error=_n_commands_utility_autopublish_error,
        remove_success=_n_commands_utility_autopublish_remove_success,
        success=_n_commands_utility_autopublish_success,
    )
    _n_commands_utility_avatar = CommandsUtilityAvatar(
        title=LocalizedString('commands.utility.avatar.title'),
    )
    _n_commands_utility_avatarDecoration_no_decoration = CommandsUtilityAvatarDecorationNo_decoration(
        description=LocalizedString('commands.utility.avatarDecoration.no_decoration.description'),
        title=LocalizedString('commands.utility.avatarDecoration.no_decoration.title'),
    )
    _n_commands_utility_avatarDecoration = CommandsUtilityAvatarDecoration(
        description=LocalizedString('commands.utility.avatarDecoration.description'),
        no_decoration=_n_commands_utility_avatarDecoration_no_decoration,
        title=LocalizedString('commands.utility.avatarDecoration.title'),
    )
    _n_commands_utility_banner = CommandsUtilityBanner(
        title=LocalizedString('commands.utility.banner.title'),
    )
    _n_commands_utility_boosterchannelinfo_info = CommandsUtilityBoosterchannelinfoInfo(
        description=LocalizedString('commands.utility.boosterchannelinfo.info.description'),
        title=LocalizedString('commands.utility.boosterchannelinfo.info.title'),
    )
    _n_commands_utility_boosterchannelinfo = CommandsUtilityBoosterchannelinfo(
        info=_n_commands_utility_boosterchannelinfo_info,
    )
    _n_commands_utility_boosterroleinfo_info = CommandsUtilityBoosterroleinfoInfo(
        description=LocalizedString('commands.utility.boosterroleinfo.info.description'),
        title=LocalizedString('commands.utility.boosterroleinfo.info.title'),
    )
    _n_commands_utility_boosterroleinfo = CommandsUtilityBoosterroleinfo(
        info=_n_commands_utility_boosterroleinfo_info,
    )
    _n_commands_utility_brawlstars_battlelog_description = CommandsUtilityBrawlstarsBattlelogDescription(
        battleTime=LocalizedString('commands.utility.brawlstars.battlelog.description.battleTime'),
        battle_time=LocalizedString('commands.utility.brawlstars.battlelog.description.battle_time'),
        duration=LocalizedString('commands.utility.brawlstars.battlelog.description.duration'),
        enemies=LocalizedString('commands.utility.brawlstars.battlelog.description.enemies'),
        enemy=LocalizedString('commands.utility.brawlstars.battlelog.description.enemy'),
        gameMap=LocalizedString('commands.utility.brawlstars.battlelog.description.gameMap'),
        gameMode=LocalizedString('commands.utility.brawlstars.battlelog.description.gameMode'),
        game_map=LocalizedString('commands.utility.brawlstars.battlelog.description.game_map'),
        game_mode=LocalizedString('commands.utility.brawlstars.battlelog.description.game_mode'),
        result=LocalizedString('commands.utility.brawlstars.battlelog.description.result'),
        starPlayer=LocalizedString('commands.utility.brawlstars.battlelog.description.starPlayer'),
        star_player=LocalizedString('commands.utility.brawlstars.battlelog.description.star_player'),
        team1=LocalizedString('commands.utility.brawlstars.battlelog.description.team1'),
        team2=LocalizedString('commands.utility.brawlstars.battlelog.description.team2'),
        teamPlayer=LocalizedString('commands.utility.brawlstars.battlelog.description.teamPlayer'),
        trophyChange=LocalizedString('commands.utility.brawlstars.battlelog.description.trophyChange'),
        trophy_change=LocalizedString('commands.utility.brawlstars.battlelog.description.trophy_change'),
    )
    _n_commands_utility_brawlstars_battlelog_error_notFound = CommandsUtilityBrawlstarsBattlelogErrorNotFound(
        description=LocalizedString('commands.utility.brawlstars.battlelog.error.notFound.description'),
        title=LocalizedString('commands.utility.brawlstars.battlelog.error.notFound.title'),
    )
    _n_commands_utility_brawlstars_battlelog_error_notLinked = CommandsUtilityBrawlstarsBattlelogErrorNotLinked(
        description=LocalizedString('commands.utility.brawlstars.battlelog.error.notLinked.description'),
        title=LocalizedString('commands.utility.brawlstars.battlelog.error.notLinked.title'),
    )
    _n_commands_utility_brawlstars_battlelog_error_userNotLinked = CommandsUtilityBrawlstarsBattlelogErrorUserNotLinked(
        description=LocalizedString('commands.utility.brawlstars.battlelog.error.userNotLinked.description'),
        title=LocalizedString('commands.utility.brawlstars.battlelog.error.userNotLinked.title'),
    )
    _n_commands_utility_brawlstars_battlelog_error = CommandsUtilityBrawlstarsBattlelogError(
        notFound=_n_commands_utility_brawlstars_battlelog_error_notFound,
        notLinked=_n_commands_utility_brawlstars_battlelog_error_notLinked,
        userNotLinked=_n_commands_utility_brawlstars_battlelog_error_userNotLinked,
    )
    _n_commands_utility_brawlstars_battlelog = CommandsUtilityBrawlstarsBattlelog(
        description=_n_commands_utility_brawlstars_battlelog_description,
        error=_n_commands_utility_brawlstars_battlelog_error,
        title=LocalizedString('commands.utility.brawlstars.battlelog.title'),
        titleNoPages=LocalizedString('commands.utility.brawlstars.battlelog.titleNoPages'),
    )
    _n_commands_utility_brawlstars_brawlers_description = CommandsUtilityBrawlstarsBrawlersDescription(
        gadget=LocalizedString('commands.utility.brawlstars.brawlers.description.gadget'),
        gadgets=LocalizedString('commands.utility.brawlstars.brawlers.description.gadgets'),
        gear=LocalizedString('commands.utility.brawlstars.brawlers.description.gear'),
        gears=LocalizedString('commands.utility.brawlstars.brawlers.description.gears'),
        maxTier=LocalizedString('commands.utility.brawlstars.brawlers.description.maxTier'),
        overview=LocalizedString('commands.utility.brawlstars.brawlers.description.overview'),
        overviewMaxTier=LocalizedString('commands.utility.brawlstars.brawlers.description.overviewMaxTier'),
        starPower=LocalizedString('commands.utility.brawlstars.brawlers.description.starPower'),
        starPowers=LocalizedString('commands.utility.brawlstars.brawlers.description.starPowers'),
        star_power=LocalizedString('commands.utility.brawlstars.brawlers.description.star_power'),
        star_powers=LocalizedString('commands.utility.brawlstars.brawlers.description.star_powers'),
    )
    _n_commands_utility_brawlstars_brawlers_error_notFound = CommandsUtilityBrawlstarsBrawlersErrorNotFound(
        _text=LocalizedString('commands.utility.brawlstars.brawlers.error.notFound'),
        description=LocalizedString('commands.utility.brawlstars.brawlers.error.notFound.description'),
        title=LocalizedString('commands.utility.brawlstars.brawlers.error.notFound.title'),
    )
    _n_commands_utility_brawlstars_brawlers_error_notLinked = CommandsUtilityBrawlstarsBrawlersErrorNotLinked(
        description=LocalizedString('commands.utility.brawlstars.brawlers.error.notLinked.description'),
        title=LocalizedString('commands.utility.brawlstars.brawlers.error.notLinked.title'),
    )
    _n_commands_utility_brawlstars_brawlers_error = CommandsUtilityBrawlstarsBrawlersError(
        notFound=_n_commands_utility_brawlstars_brawlers_error_notFound,
        notLinked=_n_commands_utility_brawlstars_brawlers_error_notLinked,
    )
    _n_commands_utility_brawlstars_brawlers_search_error = CommandsUtilityBrawlstarsBrawlersSearchError(
        description=LocalizedString('commands.utility.brawlstars.brawlers.search.error.description'),
        invalidInput=LocalizedString('commands.utility.brawlstars.brawlers.search.error.invalidInput'),
        title=LocalizedString('commands.utility.brawlstars.brawlers.search.error.title'),
    )
    _n_commands_utility_brawlstars_brawlers_search = CommandsUtilityBrawlstarsBrawlersSearch(
        error=_n_commands_utility_brawlstars_brawlers_search_error,
        label=LocalizedString('commands.utility.brawlstars.brawlers.search.label'),
        placeholder=LocalizedString('commands.utility.brawlstars.brawlers.search.placeholder'),
        title=LocalizedString('commands.utility.brawlstars.brawlers.search.title'),
    )
    _n_commands_utility_brawlstars_brawlers = CommandsUtilityBrawlstarsBrawlers(
        description=_n_commands_utility_brawlstars_brawlers_description,
        error=_n_commands_utility_brawlstars_brawlers_error,
        search=_n_commands_utility_brawlstars_brawlers_search,
        title=LocalizedString('commands.utility.brawlstars.brawlers.title'),
        titleNoPages=LocalizedString('commands.utility.brawlstars.brawlers.titleNoPages'),
    )
    _n_commands_utility_brawlstars_club_description = CommandsUtilityBrawlstarsClubDescription(
        member=LocalizedString('commands.utility.brawlstars.club.description.member'),
        overview=LocalizedString('commands.utility.brawlstars.club.description.overview'),
    )
    _n_commands_utility_brawlstars_club_error_notFound = CommandsUtilityBrawlstarsClubErrorNotFound(
        _text=LocalizedString('commands.utility.brawlstars.club.error.notFound'),
        description=LocalizedString('commands.utility.brawlstars.club.error.notFound.description'),
        title=LocalizedString('commands.utility.brawlstars.club.error.notFound.title'),
    )
    _n_commands_utility_brawlstars_club_error = CommandsUtilityBrawlstarsClubError(
        notFound=_n_commands_utility_brawlstars_club_error_notFound,
    )
    _n_commands_utility_brawlstars_club_search_error = CommandsUtilityBrawlstarsClubSearchError(
        description=LocalizedString('commands.utility.brawlstars.club.search.error.description'),
        invalidInput=LocalizedString('commands.utility.brawlstars.club.search.error.invalidInput'),
        title=LocalizedString('commands.utility.brawlstars.club.search.error.title'),
    )
    _n_commands_utility_brawlstars_club_search = CommandsUtilityBrawlstarsClubSearch(
        error=_n_commands_utility_brawlstars_club_search_error,
        label=LocalizedString('commands.utility.brawlstars.club.search.label'),
        placeholder=LocalizedString('commands.utility.brawlstars.club.search.placeholder'),
        title=LocalizedString('commands.utility.brawlstars.club.search.title'),
    )
    _n_commands_utility_brawlstars_club = CommandsUtilityBrawlstarsClub(
        description=_n_commands_utility_brawlstars_club_description,
        error=_n_commands_utility_brawlstars_club_error,
        search=_n_commands_utility_brawlstars_club_search,
        title=LocalizedString('commands.utility.brawlstars.club.title'),
        titleNoMembers=LocalizedString('commands.utility.brawlstars.club.titleNoMembers'),
    )
    _n_commands_utility_brawlstars_events_error = CommandsUtilityBrawlstarsEventsError(
        notFound=LocalizedString('commands.utility.brawlstars.events.error.notFound'),
    )
    _n_commands_utility_brawlstars_events_notFound = CommandsUtilityBrawlstarsEventsNotFound(
        description=LocalizedString('commands.utility.brawlstars.events.notFound.description'),
        title=LocalizedString('commands.utility.brawlstars.events.notFound.title'),
    )
    _n_commands_utility_brawlstars_events = CommandsUtilityBrawlstarsEvents(
        description=LocalizedString('commands.utility.brawlstars.events.description'),
        error=_n_commands_utility_brawlstars_events_error,
        notFound=_n_commands_utility_brawlstars_events_notFound,
        notYourEmbed=LocalizedString('commands.utility.brawlstars.events.notYourEmbed'),
        title=LocalizedString('commands.utility.brawlstars.events.title'),
        titleNoPages=LocalizedString('commands.utility.brawlstars.events.titleNoPages'),
    )
    _n_commands_utility_brawlstars_gameModes = CommandsUtilityBrawlstarsGameModes(
        bounty=LocalizedString('commands.utility.brawlstars.gameModes.bounty'),
        brawlBall=LocalizedString('commands.utility.brawlstars.gameModes.brawlBall'),
        brawlBall5V5=LocalizedString('commands.utility.brawlstars.gameModes.brawlBall5V5'),
        duels=LocalizedString('commands.utility.brawlstars.gameModes.duels'),
        duoShowdown=LocalizedString('commands.utility.brawlstars.gameModes.duoShowdown'),
        gemGrab=LocalizedString('commands.utility.brawlstars.gameModes.gemGrab'),
        heist=LocalizedString('commands.utility.brawlstars.gameModes.heist'),
        hotZone=LocalizedString('commands.utility.brawlstars.gameModes.hotZone'),
        knockout=LocalizedString('commands.utility.brawlstars.gameModes.knockout'),
        soloShowdown=LocalizedString('commands.utility.brawlstars.gameModes.soloShowdown'),
        unknown=LocalizedString('commands.utility.brawlstars.gameModes.unknown'),
        wipeout=LocalizedString('commands.utility.brawlstars.gameModes.wipeout'),
        wipeout5V5=LocalizedString('commands.utility.brawlstars.gameModes.wipeout5V5'),
    )
    _n_commands_utility_brawlstars_link_error_alreadyLinked = CommandsUtilityBrawlstarsLinkErrorAlreadyLinked(
        description=LocalizedString('commands.utility.brawlstars.link.error.alreadyLinked.description'),
        title=LocalizedString('commands.utility.brawlstars.link.error.alreadyLinked.title'),
    )
    _n_commands_utility_brawlstars_link_error_notFound = CommandsUtilityBrawlstarsLinkErrorNotFound(
        description=LocalizedString('commands.utility.brawlstars.link.error.notFound.description'),
        title=LocalizedString('commands.utility.brawlstars.link.error.notFound.title'),
    )
    _n_commands_utility_brawlstars_link_error = CommandsUtilityBrawlstarsLinkError(
        alreadyLinked=_n_commands_utility_brawlstars_link_error_alreadyLinked,
        notFound=_n_commands_utility_brawlstars_link_error_notFound,
    )
    _n_commands_utility_brawlstars_link_success = CommandsUtilityBrawlstarsLinkSuccess(
        description=LocalizedString('commands.utility.brawlstars.link.success.description'),
        title=LocalizedString('commands.utility.brawlstars.link.success.title'),
    )
    _n_commands_utility_brawlstars_link = CommandsUtilityBrawlstarsLink(
        error=_n_commands_utility_brawlstars_link_error,
        success=_n_commands_utility_brawlstars_link_success,
    )
    _n_commands_utility_brawlstars_maps = CommandsUtilityBrawlstarsMaps(
        Acid_Cavern_Churn=LocalizedString('commands.utility.brawlstars.maps.Acid Cavern Churn'),
        Acid_Lakes=LocalizedString('commands.utility.brawlstars.maps.Acid Lakes'),
        Backyard_Bowl=LocalizedString('commands.utility.brawlstars.maps.Backyard Bowl'),
        Beach_Ball=LocalizedString('commands.utility.brawlstars.maps.Beach Ball'),
        Belles_Rock=LocalizedString('commands.utility.brawlstars.maps.Belles Rock'),
        Broiler_Room=LocalizedString('commands.utility.brawlstars.maps.Broiler Room'),
        Canal_Grande=LocalizedString('commands.utility.brawlstars.maps.Canal Grande'),
        Cavern_Churn=LocalizedString('commands.utility.brawlstars.maps.Cavern Churn'),
        Center_Stage=LocalizedString('commands.utility.brawlstars.maps.Center Stage'),
        Cool_shapes=LocalizedString('commands.utility.brawlstars.maps.Cool shapes'),
        Crystal_Arcade=LocalizedString('commands.utility.brawlstars.maps.Crystal Arcade'),
        Dark_Passage=LocalizedString('commands.utility.brawlstars.maps.Dark Passage'),
        Deathcap_Trap=LocalizedString('commands.utility.brawlstars.maps.Deathcap Trap'),
        Deep_Forest=LocalizedString('commands.utility.brawlstars.maps.Deep Forest'),
        Double_Swoosh=LocalizedString('commands.utility.brawlstars.maps.Double Swoosh'),
        Double_Trouble=LocalizedString('commands.utility.brawlstars.maps.Double Trouble'),
        Dried_Up_River=LocalizedString('commands.utility.brawlstars.maps.Dried Up River'),
        Dueling_Beetles=LocalizedString('commands.utility.brawlstars.maps.Dueling Beetles'),
        Feast_Or_Famine=LocalizedString('commands.utility.brawlstars.maps.Feast Or Famine'),
        Final_Four=LocalizedString('commands.utility.brawlstars.maps.Final Four'),
        Flarning_Phoenix=LocalizedString('commands.utility.brawlstars.maps.Flarning Phoenix'),
        Flying_Fantasies=LocalizedString('commands.utility.brawlstars.maps.Flying Fantasies'),
        Forest_Clearing=LocalizedString('commands.utility.brawlstars.maps.Forest Clearing'),
        Four_Levels=LocalizedString('commands.utility.brawlstars.maps.Four Levels'),
        Freezig_Ripples=LocalizedString('commands.utility.brawlstars.maps.Freezig Ripples'),
        Frosty_Tracks=LocalizedString('commands.utility.brawlstars.maps.Frosty Tracks'),
        Gem_Fort=LocalizedString('commands.utility.brawlstars.maps.Gem Fort'),
        Gg_2_0=LocalizedString('commands.utility.brawlstars.maps."Gg 2.0"'),
        Goldarm_Gulch=LocalizedString('commands.utility.brawlstars.maps.Goldarm Gulch'),
        Great_Waves=LocalizedString('commands.utility.brawlstars.maps.Great Waves'),
        H_For___=LocalizedString('commands.utility.brawlstars.maps."H For..."'),
        Hard_Rock_Mine=LocalizedString('commands.utility.brawlstars.maps.Hard Rock Mine'),
        Hideout=LocalizedString('commands.utility.brawlstars.maps.Hideout'),
        Hoop_Boot_Hill=LocalizedString('commands.utility.brawlstars.maps.Hoop Boot Hill'),
        Hot_Potato=LocalizedString('commands.utility.brawlstars.maps.Hot Potato'),
        Icy_ice_park=LocalizedString('commands.utility.brawlstars.maps.Icy ice park'),
        Infinite_Doom=LocalizedString('commands.utility.brawlstars.maps.Infinite Doom'),
        Island_Invasion=LocalizedString('commands.utility.brawlstars.maps.Island Invasion'),
        Kaboom_Canyon=LocalizedString('commands.utility.brawlstars.maps.Kaboom Canyon'),
        Last_Stop=LocalizedString('commands.utility.brawlstars.maps.Last Stop'),
        Layer_Bake=LocalizedString('commands.utility.brawlstars.maps.Layer Bake'),
        Layer_Cake=LocalizedString('commands.utility.brawlstars.maps.Layer Cake'),
        Marksman_s_Paradise=LocalizedString("commands.utility.brawlstars.maps.Marksman's Paradise"),
        Minecard_Madness=LocalizedString('commands.utility.brawlstars.maps.Minecard Madness'),
        Monkey_Maze=LocalizedString('commands.utility.brawlstars.maps.Monkey Maze'),
        New_Horizons=LocalizedString('commands.utility.brawlstars.maps.New Horizons'),
        No_Excuses=LocalizedString('commands.utility.brawlstars.maps.No Excuses'),
        No_Surrender=LocalizedString('commands.utility.brawlstars.maps.No Surrender'),
        Noisy_Neighbors=LocalizedString('commands.utility.brawlstars.maps.Noisy Neighbors'),
        Open_Business=LocalizedString('commands.utility.brawlstars.maps.Open Business'),
        Open_Space=LocalizedString('commands.utility.brawlstars.maps.Open Space'),
        Out_In_The_Open=LocalizedString('commands.utility.brawlstars.maps.Out In The Open'),
        Overgrown_Ruins=LocalizedString('commands.utility.brawlstars.maps.Overgrown Ruins'),
        Parallel_Plays=LocalizedString('commands.utility.brawlstars.maps.Parallel Plays'),
        Penalty_Kick=LocalizedString('commands.utility.brawlstars.maps.Penalty Kick'),
        Petticoat_Duel=LocalizedString('commands.utility.brawlstars.maps.Petticoat Duel'),
        Pinball_Dreams=LocalizedString('commands.utility.brawlstars.maps.Pinball Dreams'),
        Pinhole_Punt=LocalizedString('commands.utility.brawlstars.maps.Pinhole Punt'),
        Quad_Damage=LocalizedString('commands.utility.brawlstars.maps.Quad Damage'),
        Ring_Of_File=LocalizedString('commands.utility.brawlstars.maps.Ring Of File'),
        Riverbank_Crossing=LocalizedString('commands.utility.brawlstars.maps.Riverbank Crossing'),
        Rockwall_Brawl=LocalizedString('commands.utility.brawlstars.maps.Rockwall Brawl'),
        Rustic_Arcade=LocalizedString('commands.utility.brawlstars.maps.Rustic Arcade'),
        Safe_Zone=LocalizedString('commands.utility.brawlstars.maps.Safe Zone'),
        Safe_r__Zone=LocalizedString('commands.utility.brawlstars.maps.Safe(r) Zone'),
        Safety_Center=LocalizedString('commands.utility.brawlstars.maps.Safety Center'),
        Second_Try=LocalizedString('commands.utility.brawlstars.maps.Second Try'),
        Shooting_Star=LocalizedString('commands.utility.brawlstars.maps.Shooting Star'),
        Shrouding_Serpent=LocalizedString('commands.utility.brawlstars.maps.Shrouding Serpent'),
        Skull_Creek=LocalizedString('commands.utility.brawlstars.maps.Skull Creek'),
        Skull_Rockwall_Brawl=LocalizedString('commands.utility.brawlstars.maps.Skull Rockwall Brawl'),
        Slayers_Paradise=LocalizedString('commands.utility.brawlstars.maps.Slayers Paradise'),
        Slippery_Road=LocalizedString('commands.utility.brawlstars.maps.Slippery Road'),
        Snake_Prairie=LocalizedString('commands.utility.brawlstars.maps.Snake Prairie'),
        Sneaky_Fields=LocalizedString('commands.utility.brawlstars.maps.Sneaky Fields'),
        Spie_Production=LocalizedString('commands.utility.brawlstars.maps.Spie Production'),
        Sunny_Soccer=LocalizedString('commands.utility.brawlstars.maps.Sunny Soccer'),
        Super_Beach=LocalizedString('commands.utility.brawlstars.maps.Super Beach'),
        Suspenders=LocalizedString('commands.utility.brawlstars.maps.Suspenders'),
        Temple_Of_Vroom=LocalizedString('commands.utility.brawlstars.maps.Temple Of Vroom'),
        The_Cooler_Hard_Rock=LocalizedString('commands.utility.brawlstars.maps.The Cooler Hard Rock'),
        The_Great_Lake=LocalizedString('commands.utility.brawlstars.maps.The Great Lake'),
        The_Great_Open=LocalizedString('commands.utility.brawlstars.maps.The Great Open'),
        Tiny_Islands=LocalizedString('commands.utility.brawlstars.maps.Tiny Islands'),
        Trickey=LocalizedString('commands.utility.brawlstars.maps.Trickey'),
        Triple_Dribble=LocalizedString('commands.utility.brawlstars.maps.Triple Dribble'),
        Two_Rivers=LocalizedString('commands.utility.brawlstars.maps.Two Rivers'),
        Undermine=LocalizedString('commands.utility.brawlstars.maps.Undermine'),
        Warrioirs_Way=LocalizedString('commands.utility.brawlstars.maps.Warrioirs Way'),
        Watersport=LocalizedString('commands.utility.brawlstars.maps.Watersport'),
        Zen_Garden=LocalizedString('commands.utility.brawlstars.maps.Zen Garden'),
    )
    _n_commands_utility_brawlstars_playerinfo_description = CommandsUtilityBrawlstarsPlayerinfoDescription(
        _3v3Victories=LocalizedString('commands.utility.brawlstars.playerinfo.description.3v3Victories'),
        brawlers=LocalizedString('commands.utility.brawlstars.playerinfo.description.brawlers'),
        club=LocalizedString('commands.utility.brawlstars.playerinfo.description.club'),
        duoVictories=LocalizedString('commands.utility.brawlstars.playerinfo.description.duoVictories'),
        expLevel=LocalizedString('commands.utility.brawlstars.playerinfo.description.expLevel'),
        highestTrophies=LocalizedString('commands.utility.brawlstars.playerinfo.description.highestTrophies'),
        highest_trophies=LocalizedString('commands.utility.brawlstars.playerinfo.description.highest_trophies'),
        soloVictories=LocalizedString('commands.utility.brawlstars.playerinfo.description.soloVictories'),
        trophies=LocalizedString('commands.utility.brawlstars.playerinfo.description.trophies'),
    )
    _n_commands_utility_brawlstars_playerinfo_error_notFound = CommandsUtilityBrawlstarsPlayerinfoErrorNotFound(
        _text=LocalizedString('commands.utility.brawlstars.playerinfo.error.notFound'),
        description=LocalizedString('commands.utility.brawlstars.playerinfo.error.notFound.description'),
        title=LocalizedString('commands.utility.brawlstars.playerinfo.error.notFound.title'),
    )
    _n_commands_utility_brawlstars_playerinfo_error_notLinked = CommandsUtilityBrawlstarsPlayerinfoErrorNotLinked(
        description=LocalizedString('commands.utility.brawlstars.playerinfo.error.notLinked.description'),
        title=LocalizedString('commands.utility.brawlstars.playerinfo.error.notLinked.title'),
    )
    _n_commands_utility_brawlstars_playerinfo_error = CommandsUtilityBrawlstarsPlayerinfoError(
        notFound=_n_commands_utility_brawlstars_playerinfo_error_notFound,
        notLinked=_n_commands_utility_brawlstars_playerinfo_error_notLinked,
    )
    _n_commands_utility_brawlstars_playerinfo = CommandsUtilityBrawlstarsPlayerinfo(
        description=_n_commands_utility_brawlstars_playerinfo_description,
        error=_n_commands_utility_brawlstars_playerinfo_error,
        title=LocalizedString('commands.utility.brawlstars.playerinfo.title'),
    )
    _n_commands_utility_brawlstars_results = CommandsUtilityBrawlstarsResults(
        defeat=LocalizedString('commands.utility.brawlstars.results.defeat'),
        draw=LocalizedString('commands.utility.brawlstars.results.draw'),
        victory=LocalizedString('commands.utility.brawlstars.results.victory'),
    )
    _n_commands_utility_brawlstars_unlink_error_notLinked = CommandsUtilityBrawlstarsUnlinkErrorNotLinked(
        description=LocalizedString('commands.utility.brawlstars.unlink.error.notLinked.description'),
        title=LocalizedString('commands.utility.brawlstars.unlink.error.notLinked.title'),
    )
    _n_commands_utility_brawlstars_unlink_error = CommandsUtilityBrawlstarsUnlinkError(
        notLinked=_n_commands_utility_brawlstars_unlink_error_notLinked,
    )
    _n_commands_utility_brawlstars_unlink_success = CommandsUtilityBrawlstarsUnlinkSuccess(
        description=LocalizedString('commands.utility.brawlstars.unlink.success.description'),
        title=LocalizedString('commands.utility.brawlstars.unlink.success.title'),
    )
    _n_commands_utility_brawlstars_unlink = CommandsUtilityBrawlstarsUnlink(
        error=_n_commands_utility_brawlstars_unlink_error,
        success=_n_commands_utility_brawlstars_unlink_success,
    )
    _n_commands_utility_brawlstars = CommandsUtilityBrawlstars(
        battlelog=_n_commands_utility_brawlstars_battlelog,
        brawlers=_n_commands_utility_brawlstars_brawlers,
        club=_n_commands_utility_brawlstars_club,
        events=_n_commands_utility_brawlstars_events,
        gameModes=_n_commands_utility_brawlstars_gameModes,
        link=_n_commands_utility_brawlstars_link,
        maps=_n_commands_utility_brawlstars_maps,
        playerinfo=_n_commands_utility_brawlstars_playerinfo,
        results=_n_commands_utility_brawlstars_results,
        unlink=_n_commands_utility_brawlstars_unlink,
    )
    _n_commands_utility_claimboosterchannel_already_claimed = CommandsUtilityClaimboosterchannelAlready_claimed(
        description=LocalizedString('commands.utility.claimboosterchannel.already_claimed.description'),
        title=LocalizedString('commands.utility.claimboosterchannel.already_claimed.title'),
    )
    _n_commands_utility_claimboosterchannel_category_not_found = CommandsUtilityClaimboosterchannelCategory_not_found(
        description=LocalizedString('commands.utility.claimboosterchannel.category_not_found.description'),
        title=LocalizedString('commands.utility.claimboosterchannel.category_not_found.title'),
    )
    _n_commands_utility_claimboosterchannel_expired = CommandsUtilityClaimboosterchannelExpired(
        reason=LocalizedString('commands.utility.claimboosterchannel.expired.reason'),
    )
    _n_commands_utility_claimboosterchannel_no_booster_channel = CommandsUtilityClaimboosterchannelNo_booster_channel(
        description=LocalizedString('commands.utility.claimboosterchannel.no_booster_channel.description'),
        title=LocalizedString('commands.utility.claimboosterchannel.no_booster_channel.title'),
    )
    _n_commands_utility_claimboosterchannel_no_booster_role = CommandsUtilityClaimboosterchannelNo_booster_role(
        description=LocalizedString('commands.utility.claimboosterchannel.no_booster_role.description'),
        title=LocalizedString('commands.utility.claimboosterchannel.no_booster_role.title'),
    )
    _n_commands_utility_claimboosterchannel_nobooster = CommandsUtilityClaimboosterchannelNobooster(
        description=LocalizedString('commands.utility.claimboosterchannel.nobooster.description'),
        title=LocalizedString('commands.utility.claimboosterchannel.nobooster.title'),
    )
    _n_commands_utility_claimboosterchannel_success = CommandsUtilityClaimboosterchannelSuccess(
        description=LocalizedString('commands.utility.claimboosterchannel.success.description'),
        reason=LocalizedString('commands.utility.claimboosterchannel.success.reason'),
        title=LocalizedString('commands.utility.claimboosterchannel.success.title'),
    )
    _n_commands_utility_claimboosterchannel = CommandsUtilityClaimboosterchannel(
        already_claimed=_n_commands_utility_claimboosterchannel_already_claimed,
        category_not_found=_n_commands_utility_claimboosterchannel_category_not_found,
        expired=_n_commands_utility_claimboosterchannel_expired,
        no_booster_channel=_n_commands_utility_claimboosterchannel_no_booster_channel,
        no_booster_role=_n_commands_utility_claimboosterchannel_no_booster_role,
        nobooster=_n_commands_utility_claimboosterchannel_nobooster,
        success=_n_commands_utility_claimboosterchannel_success,
    )
    _n_commands_utility_claimboosterrole_already_claimed = CommandsUtilityClaimboosterroleAlready_claimed(
        description=LocalizedString('commands.utility.claimboosterrole.already_claimed.description'),
        title=LocalizedString('commands.utility.claimboosterrole.already_claimed.title'),
    )
    _n_commands_utility_claimboosterrole_expired = CommandsUtilityClaimboosterroleExpired(
        reason=LocalizedString('commands.utility.claimboosterrole.expired.reason'),
    )
    _n_commands_utility_claimboosterrole_invalid_color = CommandsUtilityClaimboosterroleInvalid_color(
        description=LocalizedString('commands.utility.claimboosterrole.invalid_color.description'),
        title=LocalizedString('commands.utility.claimboosterrole.invalid_color.title'),
    )
    _n_commands_utility_claimboosterrole_no_booster_role = CommandsUtilityClaimboosterroleNo_booster_role(
        description=LocalizedString('commands.utility.claimboosterrole.no_booster_role.description'),
        title=LocalizedString('commands.utility.claimboosterrole.no_booster_role.title'),
    )
    _n_commands_utility_claimboosterrole_nobooster = CommandsUtilityClaimboosterroleNobooster(
        description=LocalizedString('commands.utility.claimboosterrole.nobooster.description'),
        title=LocalizedString('commands.utility.claimboosterrole.nobooster.title'),
    )
    _n_commands_utility_claimboosterrole_role_not_found = CommandsUtilityClaimboosterroleRole_not_found(
        description=LocalizedString('commands.utility.claimboosterrole.role_not_found.description'),
        title=LocalizedString('commands.utility.claimboosterrole.role_not_found.title'),
    )
    _n_commands_utility_claimboosterrole_success = CommandsUtilityClaimboosterroleSuccess(
        description=LocalizedString('commands.utility.claimboosterrole.success.description'),
        reason=LocalizedString('commands.utility.claimboosterrole.success.reason'),
        title=LocalizedString('commands.utility.claimboosterrole.success.title'),
    )
    _n_commands_utility_claimboosterrole = CommandsUtilityClaimboosterrole(
        already_claimed=_n_commands_utility_claimboosterrole_already_claimed,
        expired=_n_commands_utility_claimboosterrole_expired,
        invalid_color=_n_commands_utility_claimboosterrole_invalid_color,
        no_booster_role=_n_commands_utility_claimboosterrole_no_booster_role,
        nobooster=_n_commands_utility_claimboosterrole_nobooster,
        role_not_found=_n_commands_utility_claimboosterrole_role_not_found,
        success=_n_commands_utility_claimboosterrole_success,
    )
    _n_commands_utility_deleteboosterchannel_missingPermission = CommandsUtilityDeleteboosterchannelMissingPermission(
        description=LocalizedString('commands.utility.deleteboosterchannel.missingPermission.description'),
        title=LocalizedString('commands.utility.deleteboosterchannel.missingPermission.title'),
    )
    _n_commands_utility_deleteboosterchannel_no_booster_channel = CommandsUtilityDeleteboosterchannelNo_booster_channel(
        description=LocalizedString('commands.utility.deleteboosterchannel.no_booster_channel.description'),
        title=LocalizedString('commands.utility.deleteboosterchannel.no_booster_channel.title'),
    )
    _n_commands_utility_deleteboosterchannel_success = CommandsUtilityDeleteboosterchannelSuccess(
        description=LocalizedString('commands.utility.deleteboosterchannel.success.description'),
        title=LocalizedString('commands.utility.deleteboosterchannel.success.title'),
    )
    _n_commands_utility_deleteboosterchannel = CommandsUtilityDeleteboosterchannel(
        missingPermission=_n_commands_utility_deleteboosterchannel_missingPermission,
        no_booster_channel=_n_commands_utility_deleteboosterchannel_no_booster_channel,
        success=_n_commands_utility_deleteboosterchannel_success,
    )
    _n_commands_utility_deleteboosterrole_missingPermission = CommandsUtilityDeleteboosterroleMissingPermission(
        description=LocalizedString('commands.utility.deleteboosterrole.missingPermission.description'),
        title=LocalizedString('commands.utility.deleteboosterrole.missingPermission.title'),
    )
    _n_commands_utility_deleteboosterrole_no_booster_role = CommandsUtilityDeleteboosterroleNo_booster_role(
        description=LocalizedString('commands.utility.deleteboosterrole.no_booster_role.description'),
        title=LocalizedString('commands.utility.deleteboosterrole.no_booster_role.title'),
    )
    _n_commands_utility_deleteboosterrole_success = CommandsUtilityDeleteboosterroleSuccess(
        description=LocalizedString('commands.utility.deleteboosterrole.success.description'),
        title=LocalizedString('commands.utility.deleteboosterrole.success.title'),
    )
    _n_commands_utility_deleteboosterrole = CommandsUtilityDeleteboosterrole(
        missingPermission=_n_commands_utility_deleteboosterrole_missingPermission,
        no_booster_role=_n_commands_utility_deleteboosterrole_no_booster_role,
        success=_n_commands_utility_deleteboosterrole_success,
    )
    _n_commands_utility_feedback_blocked = CommandsUtilityFeedbackBlocked(
        description=LocalizedString('commands.utility.feedback.blocked.description'),
        title=LocalizedString('commands.utility.feedback.blocked.title'),
    )
    _n_commands_utility_feedback_modal_feedbackdescription = CommandsUtilityFeedbackModalFeedbackdescription(
        label=LocalizedString('commands.utility.feedback.modal.feedbackdescription.label'),
        placeholder=LocalizedString('commands.utility.feedback.modal.feedbackdescription.placeholder'),
    )
    _n_commands_utility_feedback_modal_feedbacktitle = CommandsUtilityFeedbackModalFeedbacktitle(
        label=LocalizedString('commands.utility.feedback.modal.feedbacktitle.label'),
        placeholder=LocalizedString('commands.utility.feedback.modal.feedbacktitle.placeholder'),
    )
    _n_commands_utility_feedback_modal_submitted = CommandsUtilityFeedbackModalSubmitted(
        description=LocalizedString('commands.utility.feedback.modal.submitted.description'),
        title=LocalizedString('commands.utility.feedback.modal.submitted.title'),
    )
    _n_commands_utility_feedback_modal_timeout = CommandsUtilityFeedbackModalTimeout(
        title=LocalizedString('commands.utility.feedback.modal.timeout.title'),
    )
    _n_commands_utility_feedback_modal = CommandsUtilityFeedbackModal(
        description=LocalizedString('commands.utility.feedback.modal.description'),
        feedbackdescription=_n_commands_utility_feedback_modal_feedbackdescription,
        feedbacktitle=_n_commands_utility_feedback_modal_feedbacktitle,
        not_authorized=LocalizedString('commands.utility.feedback.modal.not_authorized'),
        submitted=_n_commands_utility_feedback_modal_submitted,
        timeout=_n_commands_utility_feedback_modal_timeout,
        title=LocalizedString('commands.utility.feedback.modal.title'),
    )
    _n_commands_utility_feedback = CommandsUtilityFeedback(
        blocked=_n_commands_utility_feedback_blocked,
        modal=_n_commands_utility_feedback_modal,
    )
    _n_commands_utility_help_noCommands = CommandsUtilityHelpNoCommands(
        description=LocalizedString('commands.utility.help.noCommands.description'),
        label=LocalizedString('commands.utility.help.noCommands.label'),
    )
    _n_commands_utility_help = CommandsUtilityHelp(
        noCommands=_n_commands_utility_help_noCommands,
        noDescriptionAvailable=LocalizedString('commands.utility.help.noDescriptionAvailable'),
        parameters=LocalizedString('commands.utility.help.parameters'),
        title=LocalizedString('commands.utility.help.title'),
        titleNoPages=LocalizedString('commands.utility.help.titleNoPages'),
    )
    _n_commands_utility_listscheduled_edit_modal = CommandsUtilityListscheduledEdit_modal(
        content_label=LocalizedString('commands.utility.listscheduled.edit_modal.content_label'),
        title=LocalizedString('commands.utility.listscheduled.edit_modal.title'),
    )
    _n_commands_utility_listscheduled_edit_success = CommandsUtilityListscheduledEdit_success(
        description=LocalizedString('commands.utility.listscheduled.edit_success.description'),
        title=LocalizedString('commands.utility.listscheduled.edit_success.title'),
    )
    _n_commands_utility_listscheduled_error = CommandsUtilityListscheduledError(
        not_authorized=LocalizedString('commands.utility.listscheduled.error.not_authorized'),
    )
    _n_commands_utility_listscheduled_no_messages = CommandsUtilityListscheduledNo_messages(
        description=LocalizedString('commands.utility.listscheduled.no_messages.description'),
        title=LocalizedString('commands.utility.listscheduled.no_messages.title'),
    )
    _n_commands_utility_listscheduled_pagination = CommandsUtilityListscheduledPagination(
        page_counter=LocalizedString('commands.utility.listscheduled.pagination.page_counter'),
    )
    _n_commands_utility_listscheduled_truncated = CommandsUtilityListscheduledTruncated(
        description=LocalizedString('commands.utility.listscheduled.truncated.description'),
        title=LocalizedString('commands.utility.listscheduled.truncated.title'),
    )
    _n_commands_utility_listscheduled = CommandsUtilityListscheduled(
        cancel_button=LocalizedString('commands.utility.listscheduled.cancel_button'),
        direct_message=LocalizedString('commands.utility.listscheduled.direct_message'),
        edit_button=LocalizedString('commands.utility.listscheduled.edit_button'),
        edit_modal=_n_commands_utility_listscheduled_edit_modal,
        edit_success=_n_commands_utility_listscheduled_edit_success,
        error=_n_commands_utility_listscheduled_error,
        message_details=LocalizedString('commands.utility.listscheduled.message_details'),
        message_id=LocalizedString('commands.utility.listscheduled.message_id'),
        no_messages=_n_commands_utility_listscheduled_no_messages,
        no_repeat=LocalizedString('commands.utility.listscheduled.no_repeat'),
        pagination=_n_commands_utility_listscheduled_pagination,
        title=LocalizedString('commands.utility.listscheduled.title'),
        truncated=_n_commands_utility_listscheduled_truncated,
    )
    _n_commands_utility_messagetrackingoptin_error = CommandsUtilityMessagetrackingoptinError(
        already_opted_in=LocalizedString('commands.utility.messagetrackingoptin.error.already_opted_in'),
        title=LocalizedString('commands.utility.messagetrackingoptin.error.title'),
    )
    _n_commands_utility_messagetrackingoptin_success = CommandsUtilityMessagetrackingoptinSuccess(
        description=LocalizedString('commands.utility.messagetrackingoptin.success.description'),
        title=LocalizedString('commands.utility.messagetrackingoptin.success.title'),
    )
    _n_commands_utility_messagetrackingoptin = CommandsUtilityMessagetrackingoptin(
        error=_n_commands_utility_messagetrackingoptin_error,
        success=_n_commands_utility_messagetrackingoptin_success,
    )
    _n_commands_utility_messagetrackingoptout_error = CommandsUtilityMessagetrackingoptoutError(
        already_opted_out=LocalizedString('commands.utility.messagetrackingoptout.error.already_opted_out'),
        title=LocalizedString('commands.utility.messagetrackingoptout.error.title'),
    )
    _n_commands_utility_messagetrackingoptout_success = CommandsUtilityMessagetrackingoptoutSuccess(
        description=LocalizedString('commands.utility.messagetrackingoptout.success.description'),
        title=LocalizedString('commands.utility.messagetrackingoptout.success.title'),
    )
    _n_commands_utility_messagetrackingoptout = CommandsUtilityMessagetrackingoptout(
        error=_n_commands_utility_messagetrackingoptout_error,
        success=_n_commands_utility_messagetrackingoptout_success,
    )
    _n_commands_utility_noBanner = CommandsUtilityNoBanner(
        title=LocalizedString('commands.utility.noBanner.title'),
    )
    _n_commands_utility_removescheduled_error_no_messages = CommandsUtilityRemovescheduledErrorNo_messages(
        description=LocalizedString('commands.utility.removescheduled.error.no_messages.description'),
        title=LocalizedString('commands.utility.removescheduled.error.no_messages.title'),
    )
    _n_commands_utility_removescheduled_error_not_found = CommandsUtilityRemovescheduledErrorNot_found(
        description=LocalizedString('commands.utility.removescheduled.error.not_found.description'),
        title=LocalizedString('commands.utility.removescheduled.error.not_found.title'),
    )
    _n_commands_utility_removescheduled_error_timeout = CommandsUtilityRemovescheduledErrorTimeout(
        description=LocalizedString('commands.utility.removescheduled.error.timeout.description'),
        title=LocalizedString('commands.utility.removescheduled.error.timeout.title'),
    )
    _n_commands_utility_removescheduled_error = CommandsUtilityRemovescheduledError(
        no_messages=_n_commands_utility_removescheduled_error_no_messages,
        not_authorized=LocalizedString('commands.utility.removescheduled.error.not_authorized'),
        not_found=_n_commands_utility_removescheduled_error_not_found,
        timeout=_n_commands_utility_removescheduled_error_timeout,
    )
    _n_commands_utility_removescheduled_no_messages = CommandsUtilityRemovescheduledNo_messages(
        description=LocalizedString('commands.utility.removescheduled.no_messages.description'),
        title=LocalizedString('commands.utility.removescheduled.no_messages.title'),
    )
    _n_commands_utility_removescheduled_not_found = CommandsUtilityRemovescheduledNot_found(
        description=LocalizedString('commands.utility.removescheduled.not_found.description'),
        title=LocalizedString('commands.utility.removescheduled.not_found.title'),
    )
    _n_commands_utility_removescheduled_select = CommandsUtilityRemovescheduledSelect(
        description=LocalizedString('commands.utility.removescheduled.select.description'),
        placeholder=LocalizedString('commands.utility.removescheduled.select.placeholder'),
        title=LocalizedString('commands.utility.removescheduled.select.title'),
    )
    _n_commands_utility_removescheduled_success = CommandsUtilityRemovescheduledSuccess(
        description=LocalizedString('commands.utility.removescheduled.success.description'),
        title=LocalizedString('commands.utility.removescheduled.success.title'),
    )
    _n_commands_utility_removescheduled_timeout = CommandsUtilityRemovescheduledTimeout(
        description=LocalizedString('commands.utility.removescheduled.timeout.description'),
        title=LocalizedString('commands.utility.removescheduled.timeout.title'),
    )
    _n_commands_utility_removescheduled = CommandsUtilityRemovescheduled(
        error=_n_commands_utility_removescheduled_error,
        no_messages=_n_commands_utility_removescheduled_no_messages,
        not_found=_n_commands_utility_removescheduled_not_found,
        select=_n_commands_utility_removescheduled_select,
        success=_n_commands_utility_removescheduled_success,
        timeout=_n_commands_utility_removescheduled_timeout,
    )
    _n_commands_utility_report_accept = CommandsUtilityReportAccept(
        label=LocalizedString('commands.utility.report.accept.label'),
    )
    _n_commands_utility_report_block_reporter = CommandsUtilityReportBlock_reporter(
        label=LocalizedString('commands.utility.report.block_reporter.label'),
    )
    _n_commands_utility_report_blocked = CommandsUtilityReportBlocked(
        description=LocalizedString('commands.utility.report.blocked.description'),
        title=LocalizedString('commands.utility.report.blocked.title'),
    )
    _n_commands_utility_report_invalid_action = CommandsUtilityReportInvalid_action(
        description=LocalizedString('commands.utility.report.invalid_action.description'),
        title=LocalizedString('commands.utility.report.invalid_action.title'),
    )
    _n_commands_utility_report_new_report = CommandsUtilityReportNew_report(
        description=LocalizedString('commands.utility.report.new_report.description'),
        title=LocalizedString('commands.utility.report.new_report.title'),
    )
    _n_commands_utility_report_no_permission = CommandsUtilityReportNo_permission(
        description=LocalizedString('commands.utility.report.no_permission.description'),
        title=LocalizedString('commands.utility.report.no_permission.title'),
    )
    _n_commands_utility_report_no_reason = CommandsUtilityReportNo_reason(
        description=LocalizedString('commands.utility.report.no_reason.description'),
        title=LocalizedString('commands.utility.report.no_reason.title'),
    )
    _n_commands_utility_report_no_report_channel = CommandsUtilityReportNo_report_channel(
        description=LocalizedString('commands.utility.report.no_report_channel.description'),
        title=LocalizedString('commands.utility.report.no_report_channel.title'),
    )
    _n_commands_utility_report_reason_too_short = CommandsUtilityReportReason_too_short(
        description=LocalizedString('commands.utility.report.reason_too_short.description'),
        title=LocalizedString('commands.utility.report.reason_too_short.title'),
    )
    _n_commands_utility_report_reject = CommandsUtilityReportReject(
        label=LocalizedString('commands.utility.report.reject.label'),
    )
    _n_commands_utility_report_report_channel_not_found = CommandsUtilityReportReport_channel_not_found(
        description=LocalizedString('commands.utility.report.report_channel_not_found.description'),
        title=LocalizedString('commands.utility.report.report_channel_not_found.title'),
    )
    _n_commands_utility_report_report_sent = CommandsUtilityReportReport_sent(
        description=LocalizedString('commands.utility.report.report_sent.description'),
        title=LocalizedString('commands.utility.report.report_sent.title'),
    )
    _n_commands_utility_report_reporter_blocked = CommandsUtilityReportReporter_blocked(
        description=LocalizedString('commands.utility.report.reporter_blocked.description'),
        title=LocalizedString('commands.utility.report.reporter_blocked.title'),
    )
    _n_commands_utility_report = CommandsUtilityReport(
        accept=_n_commands_utility_report_accept,
        block_reporter=_n_commands_utility_report_block_reporter,
        blocked=_n_commands_utility_report_blocked,
        invalid_action=_n_commands_utility_report_invalid_action,
        new_report=_n_commands_utility_report_new_report,
        no_permission=_n_commands_utility_report_no_permission,
        no_reason=_n_commands_utility_report_no_reason,
        no_report_channel=_n_commands_utility_report_no_report_channel,
        reason_too_short=_n_commands_utility_report_reason_too_short,
        reject=_n_commands_utility_report_reject,
        report_channel_not_found=_n_commands_utility_report_report_channel_not_found,
        report_sent=_n_commands_utility_report_report_sent,
        reporter_blocked=_n_commands_utility_report_reporter_blocked,
    )
    _n_commands_utility_reports_accept = CommandsUtilityReportsAccept(
        label=LocalizedString('commands.utility.reports.accept.label'),
    )
    _n_commands_utility_reports_block_reporter = CommandsUtilityReportsBlock_reporter(
        label=LocalizedString('commands.utility.reports.block_reporter.label'),
    )
    _n_commands_utility_reports_blocked = CommandsUtilityReportsBlocked(
        description=LocalizedString('commands.utility.reports.blocked.description'),
        title=LocalizedString('commands.utility.reports.blocked.title'),
    )
    _n_commands_utility_reports_invalid_action = CommandsUtilityReportsInvalid_action(
        description=LocalizedString('commands.utility.reports.invalid_action.description'),
        title=LocalizedString('commands.utility.reports.invalid_action.title'),
    )
    _n_commands_utility_reports_new_report = CommandsUtilityReportsNew_report(
        description=LocalizedString('commands.utility.reports.new_report.description'),
        title=LocalizedString('commands.utility.reports.new_report.title'),
    )
    _n_commands_utility_reports_no_permission = CommandsUtilityReportsNo_permission(
        description=LocalizedString('commands.utility.reports.no_permission.description'),
        title=LocalizedString('commands.utility.reports.no_permission.title'),
    )
    _n_commands_utility_reports_no_reason = CommandsUtilityReportsNo_reason(
        description=LocalizedString('commands.utility.reports.no_reason.description'),
        title=LocalizedString('commands.utility.reports.no_reason.title'),
    )
    _n_commands_utility_reports_no_report_channel = CommandsUtilityReportsNo_report_channel(
        description=LocalizedString('commands.utility.reports.no_report_channel.description'),
        title=LocalizedString('commands.utility.reports.no_report_channel.title'),
    )
    _n_commands_utility_reports_reason_too_short = CommandsUtilityReportsReason_too_short(
        description=LocalizedString('commands.utility.reports.reason_too_short.description'),
        title=LocalizedString('commands.utility.reports.reason_too_short.title'),
    )
    _n_commands_utility_reports_reject = CommandsUtilityReportsReject(
        label=LocalizedString('commands.utility.reports.reject.label'),
    )
    _n_commands_utility_reports_report_accepted = CommandsUtilityReportsReport_accepted(
        description=LocalizedString('commands.utility.reports.report_accepted.description'),
        title=LocalizedString('commands.utility.reports.report_accepted.title'),
    )
    _n_commands_utility_reports_report_channel_not_found = CommandsUtilityReportsReport_channel_not_found(
        description=LocalizedString('commands.utility.reports.report_channel_not_found.description'),
        title=LocalizedString('commands.utility.reports.report_channel_not_found.title'),
    )
    _n_commands_utility_reports_report_rejected = CommandsUtilityReportsReport_rejected(
        description=LocalizedString('commands.utility.reports.report_rejected.description'),
        title=LocalizedString('commands.utility.reports.report_rejected.title'),
    )
    _n_commands_utility_reports_report_sent = CommandsUtilityReportsReport_sent(
        description=LocalizedString('commands.utility.reports.report_sent.description'),
        title=LocalizedString('commands.utility.reports.report_sent.title'),
    )
    _n_commands_utility_reports_reporter_blocked = CommandsUtilityReportsReporter_blocked(
        description=LocalizedString('commands.utility.reports.reporter_blocked.description'),
        title=LocalizedString('commands.utility.reports.reporter_blocked.title'),
    )
    _n_commands_utility_reports = CommandsUtilityReports(
        accept=_n_commands_utility_reports_accept,
        block_reporter=_n_commands_utility_reports_block_reporter,
        blocked=_n_commands_utility_reports_blocked,
        invalid_action=_n_commands_utility_reports_invalid_action,
        new_report=_n_commands_utility_reports_new_report,
        no_permission=_n_commands_utility_reports_no_permission,
        no_reason=_n_commands_utility_reports_no_reason,
        no_report_channel=_n_commands_utility_reports_no_report_channel,
        reason_too_short=_n_commands_utility_reports_reason_too_short,
        reject=_n_commands_utility_reports_reject,
        report_accepted=_n_commands_utility_reports_report_accepted,
        report_channel_not_found=_n_commands_utility_reports_report_channel_not_found,
        report_rejected=_n_commands_utility_reports_report_rejected,
        report_sent=_n_commands_utility_reports_report_sent,
        reporter_blocked=_n_commands_utility_reports_reporter_blocked,
    )
    _n_commands_utility_schedulemessage_invalidTime = CommandsUtilitySchedulemessageInvalidTime(
        description=LocalizedString('commands.utility.schedulemessage.invalidTime.description'),
        title=LocalizedString('commands.utility.schedulemessage.invalidTime.title'),
    )
    _n_commands_utility_schedulemessage_noBotChannelPermission = CommandsUtilitySchedulemessageNoBotChannelPermission(
        description=LocalizedString('commands.utility.schedulemessage.noBotChannelPermission.description'),
        title=LocalizedString('commands.utility.schedulemessage.noBotChannelPermission.title'),
    )
    _n_commands_utility_schedulemessage_noChannelPermission = CommandsUtilitySchedulemessageNoChannelPermission(
        description=LocalizedString('commands.utility.schedulemessage.noChannelPermission.description'),
        title=LocalizedString('commands.utility.schedulemessage.noChannelPermission.title'),
    )
    _n_commands_utility_schedulemessage_noDMPermission = CommandsUtilitySchedulemessageNoDMPermission(
        description=LocalizedString('commands.utility.schedulemessage.noDMPermission.description'),
        title=LocalizedString('commands.utility.schedulemessage.noDMPermission.title'),
    )
    _n_commands_utility_schedulemessage_noRepeatPermission = CommandsUtilitySchedulemessageNoRepeatPermission(
        description=LocalizedString('commands.utility.schedulemessage.noRepeatPermission.description'),
        title=LocalizedString('commands.utility.schedulemessage.noRepeatPermission.title'),
    )
    _n_commands_utility_schedulemessage_pastTime = CommandsUtilitySchedulemessagePastTime(
        description=LocalizedString('commands.utility.schedulemessage.pastTime.description'),
        title=LocalizedString('commands.utility.schedulemessage.pastTime.title'),
    )
    _n_commands_utility_schedulemessage_success = CommandsUtilitySchedulemessageSuccess(
        description=LocalizedString('commands.utility.schedulemessage.success.description'),
        title=LocalizedString('commands.utility.schedulemessage.success.title'),
    )
    _n_commands_utility_schedulemessage_tooManyScheduled = CommandsUtilitySchedulemessageTooManyScheduled(
        description=LocalizedString('commands.utility.schedulemessage.tooManyScheduled.description'),
        title=LocalizedString('commands.utility.schedulemessage.tooManyScheduled.title'),
    )
    _n_commands_utility_schedulemessage = CommandsUtilitySchedulemessage(
        invalidTime=_n_commands_utility_schedulemessage_invalidTime,
        noBotChannelPermission=_n_commands_utility_schedulemessage_noBotChannelPermission,
        noChannelPermission=_n_commands_utility_schedulemessage_noChannelPermission,
        noDMPermission=_n_commands_utility_schedulemessage_noDMPermission,
        noRepeatPermission=_n_commands_utility_schedulemessage_noRepeatPermission,
        pastTime=_n_commands_utility_schedulemessage_pastTime,
        referenceMessage=LocalizedString('commands.utility.schedulemessage.referenceMessage'),
        success=_n_commands_utility_schedulemessage_success,
        tooManyScheduled=_n_commands_utility_schedulemessage_tooManyScheduled,
    )
    _n_commands_utility_setupboosterchannel_already_set = CommandsUtilitySetupboosterchannelAlready_set(
        description=LocalizedString('commands.utility.setupboosterchannel.already_set.description'),
        title=LocalizedString('commands.utility.setupboosterchannel.already_set.title'),
    )
    _n_commands_utility_setupboosterchannel_missingPermission = CommandsUtilitySetupboosterchannelMissingPermission(
        description=LocalizedString('commands.utility.setupboosterchannel.missingPermission.description'),
        title=LocalizedString('commands.utility.setupboosterchannel.missingPermission.title'),
    )
    _n_commands_utility_setupboosterchannel_success = CommandsUtilitySetupboosterchannelSuccess(
        description=LocalizedString('commands.utility.setupboosterchannel.success.description'),
        title=LocalizedString('commands.utility.setupboosterchannel.success.title'),
    )
    _n_commands_utility_setupboosterchannel = CommandsUtilitySetupboosterchannel(
        already_set=_n_commands_utility_setupboosterchannel_already_set,
        missingPermission=_n_commands_utility_setupboosterchannel_missingPermission,
        success=_n_commands_utility_setupboosterchannel_success,
    )
    _n_commands_utility_setupboosterrole_already_set = CommandsUtilitySetupboosterroleAlready_set(
        description=LocalizedString('commands.utility.setupboosterrole.already_set.description'),
        title=LocalizedString('commands.utility.setupboosterrole.already_set.title'),
    )
    _n_commands_utility_setupboosterrole_missingPermission = CommandsUtilitySetupboosterroleMissingPermission(
        description=LocalizedString('commands.utility.setupboosterrole.missingPermission.description'),
        title=LocalizedString('commands.utility.setupboosterrole.missingPermission.title'),
    )
    _n_commands_utility_setupboosterrole_success = CommandsUtilitySetupboosterroleSuccess(
        description=LocalizedString('commands.utility.setupboosterrole.success.description'),
        title=LocalizedString('commands.utility.setupboosterrole.success.title'),
    )
    _n_commands_utility_setupboosterrole = CommandsUtilitySetupboosterrole(
        already_set=_n_commands_utility_setupboosterrole_already_set,
        missingPermission=_n_commands_utility_setupboosterrole_missingPermission,
        success=_n_commands_utility_setupboosterrole_success,
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_error_missingBotPermissions = CommandsUtilityTwitchAddTwitchLiveNotificationErrorMissingBotPermissions(
        description=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.error.missingBotPermissions.description'),
        title=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.error.missingBotPermissions.title'),
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_error_missingPermissions = CommandsUtilityTwitchAddTwitchLiveNotificationErrorMissingPermissions(
        description=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.error.missingPermissions.description'),
        title=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.error.missingPermissions.title'),
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_error_twitchNameNotFound = CommandsUtilityTwitchAddTwitchLiveNotificationErrorTwitchNameNotFound(
        description=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.error.twitchNameNotFound.description'),
        title=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.error.twitchNameNotFound.title'),
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_error = CommandsUtilityTwitchAddTwitchLiveNotificationError(
        missingBotPermissions=_n_commands_utility_twitch_addTwitchLiveNotification_error_missingBotPermissions,
        missingPermissions=_n_commands_utility_twitch_addTwitchLiveNotification_error_missingPermissions,
        twitchNameNotFound=_n_commands_utility_twitch_addTwitchLiveNotification_error_twitchNameNotFound,
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_errors_missingBotPermissions = CommandsUtilityTwitchAddTwitchLiveNotificationErrorsMissingBotPermissions(
        description=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.errors.missingBotPermissions.description'),
        title=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.errors.missingBotPermissions.title'),
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_errors_missingPermissions = CommandsUtilityTwitchAddTwitchLiveNotificationErrorsMissingPermissions(
        description=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.errors.missingPermissions.description'),
        title=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.errors.missingPermissions.title'),
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_errors_notYourNotification = CommandsUtilityTwitchAddTwitchLiveNotificationErrorsNotYourNotification(
        description=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.errors.notYourNotification.description'),
        title=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.errors.notYourNotification.title'),
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_errors_twitchNameNotFound = CommandsUtilityTwitchAddTwitchLiveNotificationErrorsTwitchNameNotFound(
        description=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.errors.twitchNameNotFound.description'),
        title=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.errors.twitchNameNotFound.title'),
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_errors = CommandsUtilityTwitchAddTwitchLiveNotificationErrors(
        missingBotPermissions=_n_commands_utility_twitch_addTwitchLiveNotification_errors_missingBotPermissions,
        missingPermissions=_n_commands_utility_twitch_addTwitchLiveNotification_errors_missingPermissions,
        notYourNotification=_n_commands_utility_twitch_addTwitchLiveNotification_errors_notYourNotification,
        twitchNameNotFound=_n_commands_utility_twitch_addTwitchLiveNotification_errors_twitchNameNotFound,
    )
    _n_commands_utility_twitch_addTwitchLiveNotification_success = CommandsUtilityTwitchAddTwitchLiveNotificationSuccess(
        description=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.success.description'),
        title=LocalizedString('commands.utility.twitch.addTwitchLiveNotification.success.title'),
    )
    _n_commands_utility_twitch_addTwitchLiveNotification = CommandsUtilityTwitchAddTwitchLiveNotification(
        error=_n_commands_utility_twitch_addTwitchLiveNotification_error,
        errors=_n_commands_utility_twitch_addTwitchLiveNotification_errors,
        success=_n_commands_utility_twitch_addTwitchLiveNotification_success,
    )
    _n_commands_utility_twitch_listTwitchLiveNotifications_error_missingPermissions = CommandsUtilityTwitchListTwitchLiveNotificationsErrorMissingPermissions(
        description=LocalizedString('commands.utility.twitch.listTwitchLiveNotifications.error.missingPermissions.description'),
        title=LocalizedString('commands.utility.twitch.listTwitchLiveNotifications.error.missingPermissions.title'),
    )
    _n_commands_utility_twitch_listTwitchLiveNotifications_error_noNotifications = CommandsUtilityTwitchListTwitchLiveNotificationsErrorNoNotifications(
        description=LocalizedString('commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.description'),
        title=LocalizedString('commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.title'),
    )
    _n_commands_utility_twitch_listTwitchLiveNotifications_error_notYourNotification = CommandsUtilityTwitchListTwitchLiveNotificationsErrorNotYourNotification(
        description=LocalizedString('commands.utility.twitch.listTwitchLiveNotifications.error.notYourNotification.description'),
    )
    _n_commands_utility_twitch_listTwitchLiveNotifications_error = CommandsUtilityTwitchListTwitchLiveNotificationsError(
        missingPermissions=_n_commands_utility_twitch_listTwitchLiveNotifications_error_missingPermissions,
        noNotifications=_n_commands_utility_twitch_listTwitchLiveNotifications_error_noNotifications,
        notYourNotification=_n_commands_utility_twitch_listTwitchLiveNotifications_error_notYourNotification,
    )
    _n_commands_utility_twitch_listTwitchLiveNotifications = CommandsUtilityTwitchListTwitchLiveNotifications(
        description=LocalizedString('commands.utility.twitch.listTwitchLiveNotifications.description'),
        error=_n_commands_utility_twitch_listTwitchLiveNotifications_error,
        title=LocalizedString('commands.utility.twitch.listTwitchLiveNotifications.title'),
        titleNoPages=LocalizedString('commands.utility.twitch.listTwitchLiveNotifications.titleNoPages'),
    )
    _n_commands_utility_twitch = CommandsUtilityTwitch(
        addTwitchLiveNotification=_n_commands_utility_twitch_addTwitchLiveNotification,
        defaultNotificationMessage=LocalizedString('commands.utility.twitch.defaultNotificationMessage'),
        listTwitchLiveNotifications=_n_commands_utility_twitch_listTwitchLiveNotifications,
    )
    _n_commands_utility = CommandsUtility(
        afk=_n_commands_utility_afk,
        autopublish=_n_commands_utility_autopublish,
        avatar=_n_commands_utility_avatar,
        avatarDecoration=_n_commands_utility_avatarDecoration,
        banner=_n_commands_utility_banner,
        boosterchannelinfo=_n_commands_utility_boosterchannelinfo,
        boosterroleinfo=_n_commands_utility_boosterroleinfo,
        brawlstars=_n_commands_utility_brawlstars,
        claimboosterchannel=_n_commands_utility_claimboosterchannel,
        claimboosterrole=_n_commands_utility_claimboosterrole,
        deleteboosterchannel=_n_commands_utility_deleteboosterchannel,
        deleteboosterrole=_n_commands_utility_deleteboosterrole,
        feedback=_n_commands_utility_feedback,
        help=_n_commands_utility_help,
        listscheduled=_n_commands_utility_listscheduled,
        messagetrackingoptin=_n_commands_utility_messagetrackingoptin,
        messagetrackingoptout=_n_commands_utility_messagetrackingoptout,
        noBanner=_n_commands_utility_noBanner,
        removescheduled=_n_commands_utility_removescheduled,
        report=_n_commands_utility_report,
        reports=_n_commands_utility_reports,
        schedulemessage=_n_commands_utility_schedulemessage,
        setupboosterchannel=_n_commands_utility_setupboosterchannel,
        setupboosterrole=_n_commands_utility_setupboosterrole,
        twitch=_n_commands_utility_twitch,
    )
    _n_commands = Commands(
        admin=_n_commands_admin,
        ai=_n_commands_ai,
        channel=_n_commands_channel,
        fun=_n_commands_fun,
        games=_n_commands_games,
        giveaway=_n_commands_giveaway,
        help=_n_commands_help,
        image=_n_commands_image,
        level=_n_commands_level,
        logs=_n_commands_logs,
        math=_n_commands_math,
        utility=_n_commands_utility,
    )
    return _n_commands


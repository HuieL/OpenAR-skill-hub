// OpenAR adaptation (HuieL, 2026-10-23): the upstream update check is
// removed. This module no longer spawns a checker or reaches the network;
// every receipt reports the check as unavailable ('disabled'), so no update
// notice is ever required. The upstream checker scripts and release manifest
// are not carried.

function unavailable(reason) {
  return { status: 'unavailable', installedVersion: null, availableVersion: null,
    releaseNotes: null, checkedAt: null, source: null, noticeRequired: false,
    noticeText: null, reason };
}

export function startDeliveryUpdateCheck() {
  return Promise.resolve(unavailable('disabled'));
}

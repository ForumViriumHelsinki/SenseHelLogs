export const subscriptionUrl = (uuid: string, from?: any) =>
  `api/subscriptions/${uuid}/${from ? `?values_timestamp_gt=${from}` : ''}`;

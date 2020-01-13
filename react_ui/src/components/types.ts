export type Value = {
  value: number,
  timestamp: string
}

export type AttributeSubscription = {
  description: string,
  uri: string
  attribute_id: number,
  values: Value[]
}

export type Subscription = {
  uuid: string,
  attributes: AttributeSubscription[]
}

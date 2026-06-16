// Node IO schema — mirrors backend engine/nodes/base.py + engine/dsl.py FieldSchema
export type VarType =
  | 'string'
  | 'number'
  | 'boolean'
  | 'object'
  | 'array[string]'
  | 'array[object]'
  | 'file'

export interface FieldSchema {
  name: string
  type: VarType
  required?: boolean
  description?: string
  default?: any
  value?: string | null // {{node_id.field}}
}

export interface NodeIOSpec {
  inputs: FieldSchema[]
  outputs: FieldSchema[]
}

export interface NodeCatalogItem {
  type: string
  label: string
  category: string
  icon: string
  default_io: NodeIOSpec
}

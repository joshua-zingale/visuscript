use bevy::prelude::{Entity, Commands};


pub enum Structure {
    Array
}


pub enum Action {
    None,
    CreateArray(Vec<String>),
    InsertToArray {entity: Entity, index: usize, value: String},
    SwapInArray {entity: Entity, a_index: usize, b_index: usize},
    RemoveFromArray {entity: Entity, index: usize},
    SetInArray {entity: Entity, index: usize, value: String},
    GetArrayContents {entity: Entity}
}
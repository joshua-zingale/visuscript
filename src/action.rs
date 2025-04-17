use bevy::prelude::{Entity, Commands};


pub enum Structure {
    Array
}


pub enum Action {
    Create(Structure),
    InsertToArray {entity: Entity, index: usize, value: String},
    SwapInArray {entity: Entity, a_index: usize, b_index: usize},
    RemoveFromArray {entity: Entity, index: usize},
    SetInArray {entity: Entity, index: usize, value: String},
}

impl Action {
    pub fn run(&self, commands: Commands) {
        match self {
            Action::Create(Structure) => {},
            Action::InsertToArray{entity, index, value} => {},
            _ => {panic!("Not implemented run for action")}
        }
    }
}
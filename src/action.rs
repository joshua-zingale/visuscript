use bevy::prelude::{Entity, Commands};


pub enum Structure {
    Array
}

pub enum Action {
    Create(Structure),
    Insert(Entity, String, usize),
}

impl Action {
    pub fn run(&self, commands: Commands) {
        match self {
            Action::Create(Structure) => {},
            Action::Insert(entity, value, index) => {},
        }
    }
}
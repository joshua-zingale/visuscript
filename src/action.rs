use bevy::prelude::Entity;
use serde::{Deserialize, Serialize};
use serde_json::Result;



#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "action")]
pub enum Action {
    None,
    Clear,
    CreateArray{array: Vec<String>},
    InsertToArray {entity: Entity, index: usize, value: String},
    SwapInArray {entity: Entity, a_index: usize, b_index: usize},
    PopFromArray {entity: Entity, index: usize},
    SetInArray {entity: Entity, index: usize, value: String},
    CreateArrayFromSlice {
        entity: Entity,
        begin: usize,
        end: usize,
        #[serde(default = "default_copy_slice_from_array_x")]
        x: f32,
        #[serde(default = "default_copy_slice_from_array_y")]
        y: f32,
    },
    GetArrayContents {entity: Entity},
}

fn default_copy_slice_from_array_x() -> f32 {
    0.0
}

fn default_copy_slice_from_array_y() -> f32 {
    -100.0
}


impl Action {
    pub fn from_json(json_string: &str) -> Result<Self> {
           serde_json::from_str(json_string)
    }
}
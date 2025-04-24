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
    GetArrayContents {entity: Entity}
}


impl Action {
    pub fn from_json(json_string: &str) -> Result<Self> {
           serde_json::from_str(json_string)
    }
}
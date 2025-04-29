use bevy::prelude::{Entity, Vec3};
use serde::{Deserialize, Serialize};
use serde_json::Result;



#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "action")]
pub enum Action {
    Destroy {entity: Entity},
    SetParent {
        parent: Entity,
        child: Entity,
    },
    SetTarget {
        entity: Entity,
        #[serde(default = "default_zero_vec3")]
        translation: Vec3,
        #[serde(default = "default_one_f32")]
        scale: f32,
        duration: f32,
    },
    GetPosition {
        entity: Entity,
        reference: Option<Entity>
    },
    GetValue {entity: Entity},
    CreateArray {
        array: Vec<String>,
        #[serde(default = "default_zero_vec3")]
        translation: Vec3,
        #[serde(default = "default_one_f32")]
        scale: f32,
    },
    InsertToArray {
        entity: Entity,
        index: usize,
        value: String,
        #[serde(default = "default_zero_vec3")]
        translation: Vec3,
    },
    SwapInArray {entity: Entity, a_index: usize, b_index: usize},
    PopFromArray {entity: Entity, index: usize},
    SetInArray {
        entity: Entity,
        index: usize,
        value: String,
        #[serde(default = "default_zero_vec3")]
        translation: Vec3
    },
    GetArrayContents {entity: Entity},
    GetArrayContentEntities {entity: Entity},
    GetArrayContentCoordinates {entity: Entity},
}


fn default_one_f32() -> f32 {
    1.0
}


fn default_zero_vec3()-> Vec3 {
    Vec3::new(0.0, 0.0, 0.0)
}



impl Action {
    pub fn from_json(json_string: &str) -> Result<Self> {
           serde_json::from_str(json_string)
    }
}
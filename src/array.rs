use bevy::prelude::*;

pub const ARRAY_CELL_FONT_SIZE: f32 = 32.0;
#[derive(Component)]
#[require(Transform)]
pub struct Array;

impl Array {
    pub fn new() -> (Array, Visibility, Transform) {
        (
            Array,
            Visibility::default(),
            Transform {
                translation: Vec3::new(0.0, 0.0, 0.0),
                ..default()
            },
        )
    }
}

#[derive(Component)]
#[require(Transform, Text2d)]
pub struct ArrayCell;

impl ArrayCell {
    pub fn new(value: String) -> (ArrayCell, Transform, Text2d, TextFont){
        (
            ArrayCell,
            Transform {
                translation: Vec3::new(0.0, -ARRAY_CELL_FONT_SIZE*4.0,0.0),
                ..default()
            },
            Text2d::new(value),
            TextFont {
                font_size: ARRAY_CELL_FONT_SIZE,
                ..default()
            },
        )
    }
}
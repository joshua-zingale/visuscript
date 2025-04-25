use bevy::prelude::*;
use crate::structure::Structure;

pub const ARRAY_CELL_FONT_SIZE: f32 = 32.0;
#[derive(Component)]
#[require(Transform)]
pub struct Array {
    pub elements: Vec<Entity>,
    pub num_columns: usize,
}

impl Array {
    pub fn new(elements: Vec<String>, num_columns: usize, transform: Transform, commands: &mut Commands) -> (Array, Structure, Visibility, Transform) {

        assert!(num_columns > 0);

        let elements: Vec<Entity> = elements.iter()
                    .map(|s| commands.spawn(ArrayCell::new(Vec3::new(0.0,-100.0,0.0), s.to_string())).id())
                    .collect();
        
        (
            Array {elements, num_columns},
            Structure,
            Visibility::default(),
            transform,
        )
    }

    pub fn spawn(elements: Vec<String>, num_columns: usize, transform: Transform, commands: &mut Commands) -> Entity {

        assert!(num_columns > 0);

        let elements: Vec<Entity> = elements.iter()
                    .map(|s| commands.spawn(ArrayCell::new(Vec3::new(0.0,-100.0,0.0), s.to_string())).id())
                    .collect();
        
        let entity = commands.spawn((
            Array {elements: elements.clone(), num_columns},
            Structure,
            Visibility::default(),
            transform,
        )).id();

        for element in elements {
            commands.entity(element).set_parent(entity);
        }
        entity
    }


    // pub fn push(&mut self, value: String, commands: &mut Commands) {
    //     self.insert(self.elements.len(), value, commands);
    // }

    pub fn insert(&mut self, entity: Entity, index: usize, value: String, commands: &mut Commands) {
        let element = commands.spawn(ArrayCell::new(Vec3::new(0.0,-100.0,0.0), value)).id();
        self.elements.insert(index, element);
        commands.entity(element).set_parent(entity);
        
    }

    pub fn pop(&mut self, index: usize, commands: &mut Commands) -> Entity {
        let element = self.elements.remove(index);
        commands.entity(element).remove_parent();
        commands.entity(element).despawn();

        return element;
    }

    pub fn set(&mut self, entity: Entity, index: usize, value: String, commands: &mut Commands) {
        commands.entity(self.elements[index]).remove_parent();
        commands.entity(self.elements[index]).despawn();
        let element = commands.spawn(ArrayCell::new(Vec3::new(0.0,-100.0,0.0), value)).id();
        self.elements[index] = element;
        commands.entity(element).set_parent(entity);
        
    }
}


#[derive(Component)]
pub struct ArrayCell;

impl ArrayCell {
    pub fn new(translation: Vec3, value: String) -> (ArrayCell, Transform, Text2d, TextFont) {
        (
            ArrayCell,
            Transform {
                translation: translation,
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
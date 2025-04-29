use bevy::prelude::*;

use crate::util::*;
use crate::structure::Structure;

pub const ARRAY_CELL_FONT_SIZE: f32 = 32.0;
#[derive(Component)]
#[require(Transform)]
pub struct Array {
    pub elements: Vec<Entity>,
    pub num_columns: usize,
    pub font_size: f32,
    pub alignment_duration: f32,
}

impl Array {

    pub fn spawn(elements: Vec<String>, num_columns: usize, transform: Transform, commands: &mut Commands) -> Entity {

        assert!(num_columns > 0);

        let elements: Vec<Entity> = elements.iter()
                    .map(|s| commands.spawn(ArrayCell::new(transform, s.to_string(), ARRAY_CELL_FONT_SIZE)).id())
                    .collect();
        
        let entity = commands.spawn((
            Array {elements: elements.clone(), num_columns, font_size: ARRAY_CELL_FONT_SIZE, alignment_duration: 1.0},
            Structure,
            Visibility::default(),
            transform,
        )).id();

        for element in elements {
            commands.entity(element).set_parent(entity);
        }
        entity
    }


    pub fn insert(&mut self, entity: Entity, index: usize, value: String, transform: Transform, commands: &mut Commands) -> Entity {
        let element = commands.spawn(ArrayCell::new(transform, value, self.font_size)).id();
        self.elements.insert(index, element);
        commands.entity(element).set_parent(entity).id()
    }

    pub fn pop(&mut self, index: usize, commands: &mut Commands) -> Entity {
        let element = self.elements.remove(index);
        commands.entity(element).remove_parent();
        commands.entity(element).despawn();

        return element;
    }

    pub fn set(&mut self, entity: Entity, index: usize, value: String, transform: Transform, commands: &mut Commands) {
        let element = commands.spawn(ArrayCell::new(transform, value, self.font_size)).id();
        commands.entity(self.elements[index]).insert((DespawnTimer::new(self.alignment_duration), DespawnOnTouch::new(element, self.font_size/2.0)));
        self.elements[index] = element;
        commands.entity(element).set_parent(entity);
        
    }
}


#[derive(Component)]
pub struct ArrayCell;

impl ArrayCell {
    pub fn new(transform: Transform, value: String, font_size: f32) -> (ArrayCell, Transform, Text2d, TextFont) {
        (
            ArrayCell,
            transform,
            Text2d::new(value),
            TextFont {
                font_size,
                ..default()
            },
        )
    }
}
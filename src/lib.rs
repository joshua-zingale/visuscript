use bevy::prelude::*;
use std::sync::mpsc;
use std::thread;


mod web_server;
mod action;
mod array_struct;
mod structure;
mod util;

use crate::array_struct::*;
use crate::action::*;
use crate::util::*;

pub fn init() {


    let (request_sender, request_reciever) = mpsc::channel::<Action>();
    let (data_sender, data_reciever) = mpsc::channel::<web_server::Data>();

    thread::spawn(move || {
        web_server::run(data_reciever, request_sender);
    });

    App::new()
        .add_plugins(DefaultPlugins)
        // .insert_non_send_resource(request_sender)
        .insert_non_send_resource(request_reciever)
        .insert_non_send_resource(data_sender)
        .add_systems(Startup, setup)
        // .add_systems(Update, debug_array)
        // .add_systems(Update, cursor_position)
        .add_systems(Update, (move_transforms_toward_transform_targets, move_transforms_toward_entity_targets))
        .add_systems(Update, (run_action, align_arrays).chain())
        .add_systems(Update, (mark_array_for_redraw, draw_array).chain())
        // .add_systems(Update, count)
        .add_systems(Update, (despawn_schedule, despawn_on_touch))
        .run();
}


// fn count(t: Query<&TargetTransform>) {
//     println!("{}", t.iter().len());
// }


fn run_action(
    request_receiver: NonSend<mpsc::Receiver<action::Action>>,
    data_sender: NonSend<mpsc::Sender<web_server::Data>>,
    mut commands: Commands,
    text2d_query: Query<&Text2d>,
    mut array_query: Query<&mut Array>,
    transform_query: Query<&Transform>,
    global_transform_query: Query<&GlobalTransform>,
) {

    if let Ok(action) = request_receiver.try_recv(){
        let data_to_send = match action {
            Action::Destroy {entity} => {
                commands.entity(entity).despawn_recursive();

                web_server::Data::None
            }
            Action::SetTarget {entity, translation, scale, duration} => {
                commands.entity(entity).insert(TargetTransform::new(
                    Transform {
                        translation: translation,
                        scale: Vec3::new(scale, scale, 1.0),
                        ..default()
                    },
                    Path::LinearInterpolation,
                    duration
                ));

                web_server::Data::None
            }
            Action::SetParent {child, parent} => {

                commands.entity(child).set_parent(parent);

                web_server::Data::None
            }
            Action::GetPosition {entity, reference} => {

                let global_transform = global_transform_query.get(entity).unwrap();

                web_server::Data::Vec3(match reference {
                    Some(reference) => {
                        global_transform.translation() - global_transform_query.get(reference).unwrap().translation()
                    }
                    None => {global_transform.translation()}
                })
            }
            Action::GetValue {entity} => {
                web_server::Data::Value(text2d_query.get(entity).unwrap().to_string())
            }
            Action::CreateArray{array: elements, translation, scale} => {
                let num_columns: usize = 10;
                
                let entity = Array::spawn(elements,
                    num_columns, 
                    Transform {
                        translation: translation,
                        scale: Vec3::new(scale, scale, 0.0),
                        ..default()
                    },
                    &mut commands);
                
                web_server::Data::Entity(entity)
            }
            Action::InsertToArray{entity, index, value, translation} => {
                array_query.get_mut(entity).unwrap().insert(entity, index, value, Transform {translation: translation, ..default()}, &mut commands);
                web_server::Data::None
            },
            Action::SwapInArray { entity, a_index, b_index } => {
                let mut array = array_query.get_mut(entity).unwrap();
                let tmp = array.elements[a_index];
                array.elements[a_index] = array.elements[b_index];
                array.elements[b_index] = tmp;
                web_server::Data::None
            }
            Action::PopFromArray { entity, index } => {

                let element = array_query.get_mut(entity).unwrap().pop(index, &mut commands);

                let value = text2d_query.get(element).expect("The array element must have a Text2d").to_string();

                // commands.entity(entity).remove_children(&[child]);
                web_server::Data::Value(value)
            }
            Action::SetInArray { entity, index, value, translation } => {
                array_query.get_mut(entity).unwrap().set(entity, index, value, Transform {translation, ..default()}, &mut commands);

                web_server::Data::None
            }
            Action::GetArrayContents { entity } => {
                web_server::Data::Values(
                    array_query.get(entity).unwrap()
                        .elements.clone().iter()
                        .map(|&element| text2d_query.get(element).unwrap().to_string())
                        .collect())
            }
            Action::GetArrayContentEntities { entity } => {
                web_server::Data::Entities(array_query.get(entity).unwrap().elements.clone())
            }
            Action::GetArrayContentCoordinates { entity } => {
                web_server::Data::Triplets(
                    array_query.get(entity).unwrap()
                        .elements.iter()
                        .map(|&element| global_transform_query.get(element).unwrap().translation())
                        .collect())
            }
        };

        data_sender.send(data_to_send).expect("The web-server thread must stay active.");

    }
}


// fn cursor_position(
//     q_window: Single<&Window>,
//     mut text_transform: Single<&mut Transform, With<Array>>,
//     camera_query: Single<(&Camera, &GlobalTransform)>
// ) {

//     let (camera, camera_transform) = camera_query.into_inner();

//     // Games typically only have one window (the primary window)
//     if let Some(position) = q_window.cursor_position() {

//         // println!("Cursor is inside the primary window, at {:?}", position);
//         let camera_pos = camera.world_to_viewport_with_depth(camera_transform, position.extend(1.0)).unwrap();
//         let camera_pos = camera_pos - Vec3::new(q_window.width(), 0.0, 0.0);
//         // println!("{:?}", camera_pos);

//         text_transform.translation = camera_pos;
//     }
// }

#[derive(Component, Debug, Clone, Copy)]
pub struct ArrayBackground;

#[derive(Component, Debug, Clone, Copy)]
pub struct ArrayOutline;

#[derive(Component, Debug, Clone, Copy)]
pub struct NeedsRedraw;


fn setup(
    mut commands: Commands,
    // request_sender: NonSendMut<mpsc::Sender<Action>>,
) {
    commands.spawn(Camera2d);
}

fn mark_array_for_redraw(
    mut commands: Commands,
    entity_query: Query<Entity, (Changed<Array>, Without<NeedsRedraw>)>,
) {
    for entity in &entity_query {
        commands.entity(entity).insert(NeedsRedraw);
    }
}

fn draw_array(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
    array_query: Query<(Entity, &Array, &Children), With<NeedsRedraw>>,
    drawing_query: Query<Entity, Or<(With<ArrayBackground>, With<ArrayOutline>)>>,

) {
    for (array_entity, array, children) in &array_query {
        // Despawn existing background and dividers for this array
        for &entity in children.iter().filter(|&&entity| drawing_query.contains(entity)) {
            commands.entity(entity).despawn_recursive();
        }

        let length = array.elements.len() as f32;
        let element_width = array.font_size; // Assuming font_size can represent element width

        // Draw the background
        commands.entity(array_entity).with_children(|parent| {
            

            // Draw the dividers
            for i in 0..array.elements.len() {
                parent.spawn((
                    ArrayBackground,
                    Mesh2d(meshes.add(Rectangle::new(element_width, array.font_size))),
                    MeshMaterial2d(materials.add(Color::srgb(0.3 - 0.05 * (i % 2) as f32, 0.3 - 0.05 * (i % 2) as f32, 0.3 - 0.05 * (i % 2) as f32))),
                    Transform::from_translation(Vec3::new(element_width * (i as f32), 0.0, -1.0)), // Ensure background is behind elements
                ));
            }

            // let outline_thickness = 2.0;
            // parent.spawn((
            //     ArrayOutline,
            //     Mesh2d(meshes.add(Rectangle::new(element_width * length + outline_thickness * 2.0, array.font_size + outline_thickness * 2.0))),
            //     MeshMaterial2d(materials.add(Color::srgb(0.7, 0.7, 0.7))),
            //     Transform::from_translation(Vec3::new(
            //             element_width * (length - 1.0) / 2.0,
            //             0.0,
            //             -2.0,
            //         ))
            // ));
        });
        

        // Remove the NeedsRedraw marker
        commands.entity(array_entity).remove::<NeedsRedraw>();
    }
}

// fn draw_array(
//     array_transform_query: Query<(&Array, &Transform)>,
//     mut meshes: ResMut<Assets<Mesh>>,
//     mut materials: ResMut<Assets<ColorMaterial>>,
//     mut commands: Commands,
// ) {
//     for (array, transform) in &array_transform_query {
            
//             let length = array.elements.len() as f32;
//             commands.spawn((
//                 Mesh2d(meshes.add(Rectangle::new(array.font_size * length, array.font_size))),
//                 MeshMaterial2d(materials.add(Color::srgb(0.3,0.3,0.3))),
//                 Transform {
//                     translation: transform.translation + Vec3::new(array.font_size*(length - 1.0)/2.0, 0.0, 0.0),
//                     ..default()
//                 },
//             ));
    
//     }
// }


fn move_transforms_toward_entity_targets(
    time: Res<Time>,
    mut commands: Commands,
    mut query: Query<(Entity, &mut TargetEntity)>,
    mut transform_query: Query<(&mut Transform, &GlobalTransform)>,
) {
    let time_delta = time.delta_secs();

    for (entity, mut target_entity) in &mut query {

        target_entity.time_passed = target_entity.time_passed + time_delta;


        let [(mut transform, _global_transform), (target_transform, _target_global_transform)] = transform_query.get_many_mut([entity, target_entity.entity]).expect("Both the entity and its target must have transforms");

        // let global_target = (target_global_transform.translation() - global_transform.translation());

        // let local_target = transform.translation + global_target;
        
        // let target_transform= transform_query.get(target_entity.entity).expect("Target entity must have a transform component");
        let progress = target_entity.get_progress();

        // let transform: Mut<'_, Transform> = transform_query.get_mut(entity).expect("");

        transform.translation = if progress < 1.0 {
            match target_entity.path {
                Path::LinearInterpolation =>  target_transform.translation * progress + transform.translation * (1.0 - progress)
            }
        }
        else {
            commands.entity(entity).remove::<TargetEntity>();
            target_transform.translation
        }
    }
}

fn move_transforms_toward_transform_targets(
    time: Res<Time>,
    mut commands: Commands,
    mut query: Query<(Entity, &mut Transform, &mut TargetTransform)>
) {
    let time_delta = time.delta_secs();

    for (entity, mut transform, mut target) in &mut query {
   
        target.time_passed = target.time_passed + time_delta;

        let progress = target.get_progress();

        transform.translation = if progress < 1.0 {
            match target.path {
                Path::LinearInterpolation => target.transform.translation * progress + transform.translation * (1.0 - progress)
            }
        }
        else {
            commands.entity(entity).remove::<TargetTransform>();
            target.transform.translation
        }
    }
}

// fn set_array_cell_parents(
//     array_query: Query<(Entity, &Array)>,
//     mut commands: Commands,
//     world: &World
// ) {
//     for (entity, array) in &array_query {
//         for element in array.elements.clone() {
//             if world.get_entity(entity).is_ok() {
//                 commands.entity(element).set_parent(entity);
//             }
//         }
//     }

// }


fn align_arrays(
    array_query: Query<&Array>,
    target_transform_query: Query<&TargetTransform>,
    mut commands: Commands,
) {
    for array in &array_query {
        align_to_grid(array.elements.as_slice(), array.font_size, array.font_size, array.num_columns, array.alignment_duration, &target_transform_query, &mut commands);
    }
}


fn align_to_grid(entities: &[Entity],  cell_width: f32, cell_height: f32, num_columns: usize, alignment_duration: f32, target_transform_query: &Query<&TargetTransform>, commands: &mut Commands) {
    let mut index = 0;

    // let length = cell_width * (if num_columns > entities.len() {num_columns} else {entities.len()} as f32);
    // let height = cell_height * ((entities.len() / num_columns + 1) as f32);

    // let offset = Vec3::new(length/2.0, height/2.0, 0.0);


    for &entity in entities.iter() {
        let target_transform = TargetTransform::new(
            Transform {
                translation: get_grid_position_row_wise(index, cell_width, cell_height, num_columns),
                ..default()
            },
            Path::LinearInterpolation,
            alignment_duration
        );

        index += 1;

        if let Ok(existing_target) = target_transform_query.get(entity) {
            if target_transform.transform == existing_target.transform {
                continue // do not update transform if it has the same target as what already exists
            }
        }

        commands.entity(entity).insert(target_transform);
    }
}


fn get_grid_position_row_wise(
    index: usize,
    cell_width: f32,
    cell_height: f32,
    num_columns: usize) -> Vec3 {

        let column_index = (index % num_columns) as f32;
        let row_index = (index / num_columns) as f32;


        Vec3::new(
            column_index * cell_width,
            -row_index * cell_height,
            0.0,
        )
}



fn despawn_on_touch(
    despawn_query: Query<(Entity, &DespawnOnTouch)>,
    transform_query: Query<&GlobalTransform>,
    mut commands: Commands
) {
    for (entity, DespawnOnTouch {entity: other, radius}) in &despawn_query {

        let [entity_transform, other_transform] = transform_query.get_many([entity, *other]).unwrap();

        if entity_transform.translation().distance(other_transform.translation()) <= *radius {
            commands.entity(entity).remove_parent();
            commands.entity(entity).despawn();
        }

    }
}



fn despawn_schedule(
    time: Res<Time>,
    mut despawn_query: Query<(Entity, &mut DespawnTimer)>,
    mut commands: Commands
) {
    let delta = time.delta_secs();

    for (entity, mut timer) in despawn_query.iter_mut() {
        timer.tick(delta);

        if timer.done() {
            commands.entity(entity).remove_parent();
            commands.entity(entity).despawn();
        }
    }
}








enum Path {
    LinearInterpolation
}


#[derive(Component)]
struct TargetEntity {
    entity: Entity,
    path: Path,
    duration: f32,
    time_passed: f32,
}

impl TargetEntity {
    fn _new(entity: Entity, path: Path) -> Self {
        Self {
            entity,
            path: path,
            duration: 1.0,
            time_passed: 0.0,
        }
    }
    fn get_progress(&self) -> f32 {
        if self.time_passed >= self.duration {
            1.0
        }
        else {
            self.time_passed/self.duration            
        }
    }
}

#[derive(Component)]
struct TargetTransform {
    transform: Transform,
    path: Path,
    duration: f32,
    time_passed: f32,
}

impl TargetTransform {
    fn new(transform: Transform, path: Path, duration: f32) -> Self {
        Self {
            transform,
            path,
            duration,
            time_passed: 0.0,
        }
    }
    fn get_progress(&self) -> f32 {
        if self.time_passed >= self.duration {
            1.0
        }
        else {
            self.time_passed/self.duration            
        }
    }
}



// #[derive(Event)]
// struct AlignToGridEvent {
//     entities: Vec<Entity>,
//     width: f32,
//     height: f32,
//     num_columns: usize
// }
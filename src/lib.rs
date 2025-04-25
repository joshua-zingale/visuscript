use bevy::prelude::*;
use std::sync::mpsc;
use std::thread;


mod web_server;
mod action;
mod array_struct;
mod structure;

use crate::array_struct::*;
use crate::action::*;
use crate::structure::Structure;


pub fn init() {


    let (request_sender, request_reciever) = mpsc::channel::<Action>();
    let (data_sender, data_reciever) = mpsc::channel::<(u64, web_server::Data)>();

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
        .add_systems(Update, run_action)
        .add_systems(Update, (move_transforms_toward_transform_targets, move_transforms_toward_entity_targets))
        .add_systems(Update, (align_arrays).chain())
        // .add_systems(Update, count)
        .add_systems(Update, replace_children)
        .run();
}


// fn count(t: Query<&TargetTransform>) {
//     println!("{}", t.iter().len());
// }

#[derive(Component)]
struct Head;

fn run_action(
    request_receiver: NonSend<mpsc::Receiver<action::Action>>,
    data_sender: NonSend<mpsc::Sender<(u64, web_server::Data)>>,
    mut commands: Commands,
    text2d_query: Query<&Text2d>,
    mut array_query: Query<&mut Array>,
    head_entity_query: Query<Entity, With<Head>>,
) {

    if let Ok(action) = request_receiver.try_recv(){
        let data_to_send = match action {
            Action::Clear => {
                for entity in &head_entity_query {
                    commands.entity(entity).despawn_recursive();
                }

                (0, web_server::Data::None)
            }
            Action::CreateArray{array: elements} => {
                let num_columns: usize = elements.len();
                
                let entity = Array::spawn(elements,
                    num_columns, 
                    Transform::default(),
                    &mut commands);

                commands.entity(entity).insert(Head);
                
                (1000, web_server::Data::Entity(entity))
            },
            Action::InsertToArray{entity, index, value} => {
                array_query.get_mut(entity).unwrap().insert(entity, index, value, &mut commands);
                (1000, web_server::Data::None)
            },
            Action::SwapInArray { entity, a_index, b_index } => {
                let mut array = array_query.get_mut(entity).unwrap();
                let tmp = array.elements[a_index];
                array.elements[a_index] = array.elements[b_index];
                array.elements[b_index] = tmp;
                (1000, web_server::Data::None)
            }
            Action::PopFromArray { entity, index } => {

                let element = array_query.get_mut(entity).unwrap().pop(index, &mut commands);

                let value = text2d_query.get(element).expect("The array element must have a Text2d").to_string();

                // commands.entity(entity).remove_children(&[child]);
                (1000, web_server::Data::Value(value))
            }
            Action::SetInArray {entity, index, value} => {
                array_query.get_mut(entity).unwrap().set(entity, index, value, &mut commands);

                (1000, web_server::Data::None)
            }
            Action::CreateArrayFromSlice {entity, begin, end, x, y} => {
                assert!(begin < end);

                let mut elements = vec![];
                for value in array_query.get_mut(entity).unwrap().elements.iter().enumerate().filter(|(i, _)| begin <= *i && *i < end).map(|(_, element)| text2d_query.get(*element).unwrap().to_string()) {
                    elements.push(value);
                }
                

                let new_entity = Array::spawn(
                    elements,
                    end - begin,
                    Transform {
                        translation: Vec3::new(0.0,0.0,0.0),
                        scale: Vec3::new(0.75, 0.75, 1.0),
                        ..default()
                    },
                    &mut commands);

                commands.entity(new_entity).insert(TargetTransform::new(
                    Transform {
                        translation: Vec3::new(x, y, 0.0),
                        ..default()
                    },
                    Path::LinearInterpolation
                ));
                
                commands.entity(new_entity).set_parent(entity);

                (1000, web_server::Data::Entity(new_entity))
            }
            Action::GetArrayContents { entity } => {
                (0, web_server::Data::Vector(
                    array_query.get(entity).unwrap()
                        .elements.clone().iter()
                        .map(|&element| text2d_query.get(element).unwrap().to_string())
                        .collect()
                ))
            }
            Action::None => {(0, web_server::Data::None)}
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

fn setup(
    mut commands: Commands,
    // request_sender: NonSendMut<mpsc::Sender<Action>>,
) {
    commands.spawn(Camera2d);
}


fn replace_children(
    time: Res<Time>,
    mut commands: Commands,
    mut child_replacement_query: Query<(Entity, &mut ReplaceTextTimer)>,
    mut text2d_query: Query<&mut Text2d>,
) {
    let delta = time.delta_secs();
    for (replacement_entity, mut child_replacement) in child_replacement_query.iter_mut() {
        child_replacement.tick(delta);

        if child_replacement.done() {
            
            let [replacer_text, mut replacee_text] = text2d_query.get_many_mut([child_replacement.replacer, child_replacement.replacee]).expect("Entities must have text2d components");

            replacee_text.clear();
            replacee_text.push_str(replacer_text.as_str());
            commands.entity(child_replacement.replacer).despawn();
            commands.entity(replacement_entity).despawn();
            
        }
    }
}

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
        align_to_grid(array.elements.as_slice(), array.num_columns, &target_transform_query, &mut commands);
    }
}


fn align_to_grid(enities: &[Entity],  num_columns: usize, target_transform_query: &Query<&TargetTransform>, commands: &mut Commands) {
    let mut index = 0;
    for &entity in enities.iter() {
        let target_transform = TargetTransform::new(
            Transform {
                translation: get_grid_position_row_wise(index, ARRAY_CELL_FONT_SIZE, ARRAY_CELL_FONT_SIZE, num_columns),
                ..default()
            },
            Path::LinearInterpolation
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


// fn debug_array(
//     keyboard_input: Res<ButtonInput<KeyCode>>,
//     array_query: Query<Entity, With<Array>>,
//     request_sender: NonSendMut<mpsc::Sender<Action>>,
// ) {

//     if keyboard_input.just_pressed(KeyCode::KeyC) {
//         request_sender.send(Action::CreateArray(vec![])).unwrap();
//     }

//     for array in array_query.iter() {
//         if keyboard_input.just_pressed(KeyCode::Digit0) {
//             request_sender.send(Action::InsertToArray { entity: array, value: "0".to_string(), index: 0}).unwrap();
//         }
//         if keyboard_input.just_pressed(KeyCode::Digit1) {
//             request_sender.send(Action::InsertToArray { entity: array, value: "1".to_string(), index: 1}).unwrap();
//         }
//         if keyboard_input.just_pressed(KeyCode::Digit2) {
//             request_sender.send(Action::InsertToArray { entity: array, value: "2".to_string(), index: 2}).unwrap();
//         }
//         if keyboard_input.just_pressed(KeyCode::Digit3) {
//             request_sender.send(Action::InsertToArray { entity: array, value: "3".to_string(), index: 3}).unwrap();
//         }
//         if keyboard_input.just_pressed(KeyCode::Digit7) {
//             request_sender.send(Action::InsertToArray { entity: array, value: "7".to_string(), index: 0}).unwrap();
//         }
//         if keyboard_input.just_pressed(KeyCode::KeyR) {
//             request_sender.send(Action::RemoveFromArray { entity: array, index: 4}).unwrap();
//         }
    
//         if keyboard_input.just_pressed(KeyCode::KeyS) {
//             request_sender.send(Action::SwapInArray{entity: array, a_index: 1, b_index: 4}).unwrap();
//         }

//         if keyboard_input.just_pressed(KeyCode::KeyE) {
//             request_sender.send(Action::SetInArray {entity: array, index: 0, value: "E".to_string()}).unwrap();
//         }
//     }
// }

#[derive(Component)]
struct ReplaceTextTimer {
    replacer: Entity,
    replacee: Entity,
    time: f32,
}

impl ReplaceTextTimer {
    fn tick(&mut self, delta: f32) {
        self.time =  match self.time {
            ..=0.0 => 0.0,
            t => t - delta,
        };
    }
    fn done(&self) -> bool{
        self.time <= 0.0
    }
}






enum Path {
    LinearInterpolation
}


#[derive(Component)]
struct TargetEntity {
    entity: Entity,
    path: Path,
    total_time: f32,
    time_passed: f32,
}

impl TargetEntity {
    fn _new(entity: Entity, path: Path) -> Self {
        Self {
            entity,
            path: path,
            total_time: 1.0,
            time_passed: 0.0,
        }
    }
    fn get_progress(&self) -> f32 {
        if self.time_passed >= self.total_time {
            1.0
        }
        else {
            self.time_passed/self.total_time            
        }
    }
}

#[derive(Component)]
struct TargetTransform {
    transform: Transform,
    path: Path,
    total_time: f32,
    time_passed: f32,
}

impl TargetTransform {
    fn new(transform: Transform, path: Path) -> Self {
        Self {
            transform: transform,
            path: path,
            total_time: 1.0,
            time_passed: 0.0,
        }
    }
    fn get_progress(&self) -> f32 {
        if self.time_passed >= self.total_time {
            1.0
        }
        else {
            self.time_passed/self.total_time            
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
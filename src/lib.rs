// use visuscript::*;
use bevy::prelude::*;
// use std::net::TcpListener;
use std::sync::mpsc;
use std::thread;


mod web_server;
mod action;
mod array;

use crate::array::*;
use crate::action::*;


pub fn init() {


    let (request_sender, request_reciever) = mpsc::channel::<Action>();
    let (data_sender, data_reciever) = mpsc::channel::<Entity>();

    // thread::spawn(move || {
    //     web_server::run(data_reciever, request_sender);
    // });

    App::new()
        .add_plugins(DefaultPlugins)
        .insert_non_send_resource(request_sender)
        .insert_non_send_resource(request_reciever)
        .insert_non_send_resource(data_sender)
        .add_systems(Startup, setup)
        // .add_systems(Update, cursor_position)
        .add_systems(Update, (debug_array, align_arrays).chain())
        .add_systems(Update, (move_transforms_toward_transform_targets, move_transforms_toward_entity_targets))
        .add_systems(Update, run_action)
        .run();
}



fn run_action(
    request_receiver: NonSend<mpsc::Receiver<action::Action>>,
    request_sender: NonSend<mpsc::Sender<Entity>>,
    mut commands: Commands,
    mut children_query: Query<&mut Children, With<Array>>,
    mut parent_query: Query<&mut Parent, With<Array>>,
) {

    if let Ok(r) = request_receiver.try_recv(){
        let entity = match r {
            Action::Create(Structure::Array) => {
                commands.spawn((TransformAnchor, Transform::default(), Visibility::default())).with_child(Array::new()).id()
            },
            Action::InsertToArray{entity, index, value} => {
                let cell = commands.spawn(ArrayCell::new(value)).id();
                commands.entity(entity).insert_children(index, &[cell]);
                entity
            },
            Action::SwapInArray { entity, a_index, b_index } => {
                children_query.get_mut(entity).unwrap().swap(a_index, b_index);
                entity
            }
            Action::RemoveFromArray { entity, index } => {

                let children: Vec<&Entity> = children_query.get(entity).unwrap().iter().collect();
                let &child = children[index];

                commands.entity(entity).remove_children(&[child]);
                commands.entity(child).despawn();
                entity
            }
            Action::SetInArray {entity, index, value} => {

                let children: Vec<&Entity> = children_query.get(entity).expect("The array entity must have children").iter().collect();
                let &child = children[index];
                let parent = parent_query.get(entity).expect("The array entity must have an anchoring parent").get();
                
                let new_entity = commands.spawn((
                    Text2d::new(value),
                    Transform {translation: Vec3::new(-50.0, -100.0, 0.0 ), ..default()},
                    TargetEntity::new(child, Path::LinearInterpolation)
                )).id();
                commands.entity(parent).add_child(new_entity);



                entity
            }
            _ => {panic!("Not implemented for debug_http!");}
        };

        request_sender.send(entity);

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
    request_sender: NonSendMut<mpsc::Sender<Action>>,
) {
    commands.spawn(Camera2d);
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


        let [(mut transform, global_transform), (target_transform, target_global_transform)] = transform_query.get_many_mut([entity, target_entity.entity]).expect("Both the entity and its target must have transforms");

        // let offset = transform.translation + (target_global_transform.translation() - global_transform.translation()) * global_transform.scale();
        
        // let target_transform= transform_query.get(target_entity.entity).expect("Target entity must have a transform component");
        let progress = target_entity.get_progress();

        // let transform: Mut<'_, Transform> = transform_query.get_mut(entity).expect("");

        transform.translation = if progress < 1.0 {
            match target_entity.path {
                Path::LinearInterpolation => target_transform.translation * progress + transform.translation * (1.0 - progress)
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


fn align_arrays(
    children_set_query: Query<&Children, (With<Array>, Changed<Children>)>,
    mut commands: Commands,
) {
    for children in &children_set_query {
        let children: Vec<&Entity> = children.iter().collect();
        let mut index = 0;
        for &child in children {
            let transform_target = TargetTransform::new(
                Transform {
                    translation: get_grid_position_row_wise(index, ARRAY_CELL_FONT_SIZE, ARRAY_CELL_FONT_SIZE, 5),
                    ..default()
                },
                Path::LinearInterpolation
            );
            commands.entity(child).insert(transform_target);
            index += 1;
        }
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


fn debug_array(
    keyboard_input: Res<ButtonInput<KeyCode>>,
    array_query: Query<Entity, With<Array>>,
    request_sender: NonSendMut<mpsc::Sender<Action>>,
) {

    if keyboard_input.just_pressed(KeyCode::KeyC) {
        request_sender.send(Action::Create(Structure::Array)).unwrap();
    }

    for array in array_query.iter() {
        if keyboard_input.just_pressed(KeyCode::Digit0) {
            request_sender.send(Action::InsertToArray { entity: array, value: "0".to_string(), index: 0}).unwrap();
        }
        if keyboard_input.just_pressed(KeyCode::Digit1) {
            request_sender.send(Action::InsertToArray { entity: array, value: "1".to_string(), index: 1}).unwrap();
        }
        if keyboard_input.just_pressed(KeyCode::Digit2) {
            request_sender.send(Action::InsertToArray { entity: array, value: "2".to_string(), index: 2}).unwrap();
        }
        if keyboard_input.just_pressed(KeyCode::Digit3) {
            request_sender.send(Action::InsertToArray { entity: array, value: "3".to_string(), index: 3}).unwrap();
        }
        if keyboard_input.just_pressed(KeyCode::Digit7) {
            request_sender.send(Action::InsertToArray { entity: array, value: "7".to_string(), index: 0}).unwrap();
        }
        if keyboard_input.just_pressed(KeyCode::KeyR) {
            request_sender.send(Action::RemoveFromArray { entity: array, index: 4}).unwrap();
        }
    
        if keyboard_input.just_pressed(KeyCode::KeyS) {
            request_sender.send(Action::SwapInArray{entity: array, a_index: 1, b_index: 4}).unwrap();
        }

        if keyboard_input.just_pressed(KeyCode::KeyE) {
            request_sender.send(Action::SetInArray {entity: array, index: 0, value: "E".to_string()}).unwrap();
        }

    }
   
}


#[derive(Component)]
struct TransformAnchor;


type InterpolationFn = fn(Vec3, Vec3, f32) -> Vec3;
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
    fn new(entity: Entity, path: Path) -> Self {
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




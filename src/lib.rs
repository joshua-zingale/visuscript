// use visuscript::*;
use bevy::prelude::*;
// use std::net::TcpListener;
use std::sync::mpsc;
use std::thread;


mod web_server;
mod action;
mod array;

use crate::array::*;

pub fn init() {

    let (request_sender, request_reciever) = mpsc::channel();

    thread::spawn(move || {
        web_server::run(request_sender)
    });

    App::new()
        .add_plugins(DefaultPlugins)
        // .insert_non_send_resource(request_reciever)
        .add_event::<InsertToArrayEvent>()
        .add_event::<RemoveFromArrayEvent>()
        .add_event::<SwapInArrayEvent>()
        .add_systems(Startup, setup)
        // .add_systems(Update, cursor_position)
        .add_systems(Update, (debug_array, insert_to_arrays, remove_from_arrays, swap_in_arrays, align_arrays, move_transforms_toward_transform_targets).chain())
        // .add_systems(Update, move_text)
        .run();
}



// fn debug_http(
//     rx: NonSend<mpsc::Receiver<i32>>,
//     array: Single<Entity, With<Array>>,
//     mut ev_inserts: EventWriter<InsertToArrayEvent>
// ) {
//     let array = array.into_inner();
//     while let Ok(r) = rx.try_recv() {
//         ev_inserts.send(InsertToArrayEvent { entity: array, value: "h".to_string(), index: 0 });
//         println!("HERE!lsls");
//     }
// }


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

fn setup(mut commands: Commands) {

    commands.spawn(Camera2d);
    

    let array = commands.spawn(Array::new()).id();

    let cell2 = commands.spawn(ArrayCell::new("1".to_string())).id();

    commands.entity(array).add_children(&[cell2]);

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

        transform.translation = if progress >= 1.0 {
            commands.entity(entity).remove::<TargetTransform>();
            target.transform.translation
        }
        else {
            match target.path {
                Path::LinearInterpolation => target.transform.translation * progress + transform.translation * (1.0 - progress)
            }
        }
    }
}

#[derive(Event, Debug)]
struct InsertToArrayEvent {
    entity: Entity,
    value: String,
    index: usize,
}

#[derive(Event, Debug)]
struct RemoveFromArrayEvent {
    entity: Entity,
    index: usize,
}

#[derive(Event, Debug)]
struct SwapInArrayEvent {
    entity: Entity,
    index1: usize,
    index2: usize,
}



fn align_arrays(
    children_set_query: Query<&Children, (With<Array>, Changed<Children>)>,
    mut commands: Commands,
) {
    for children in &children_set_query {
        let children: Vec<&Entity> = children.iter().collect();
        let num_children = children.len();
        let mut next_x = -(num_children as f32) * ARRAY_CELL_FONT_SIZE;
        for child in children {
            let transform_target = TargetTransform::new(
                &Transform {
                    translation: Vec3::new(next_x, 0.0, 0.0),
                    ..default()
                },
                Path::LinearInterpolation
            );
            commands.entity(*child).insert(transform_target);
            next_x += ARRAY_CELL_FONT_SIZE * 2.0;
        }
    }
}

fn insert_to_arrays(
    mut commands: Commands,
    mut ev_inserts: EventReader<InsertToArrayEvent>,
    // children_query: Query<&Children, (Changed<Children>, With<Array>)>,
    
) {
    for insertion in ev_inserts.read() {
        let cell = commands.spawn(ArrayCell::new(insertion.value.clone())).id();
        commands.entity(insertion.entity).insert_children(insertion.index, &[cell]);
    }
}

fn remove_from_arrays(
    mut commands: Commands,
    mut ev_removals: EventReader<RemoveFromArrayEvent>,
    children_query: Query<&Children, With<Array>>
) {
    // let removals: Vec<&RemoveFromArrayEvent> = ev_removals.read().collect();
    
    for removal in ev_removals.read() {

        let children: Vec<&Entity> = children_query.get(removal.entity).unwrap().iter().collect();

        let child = children[removal.index];

        commands.entity(removal.entity).remove_children(&[*child]);

        commands.entity(*child).despawn();

    }
}

fn swap_in_arrays(
    mut ev_swaps: EventReader<SwapInArrayEvent>,

    mut children_query: Query<&mut Children, With<Array>>,
) {

    for swap in ev_swaps.read() {

        // let mut children: Vec<&Entity> = children_query.get(swap.entity).unwrap().iter().collect();
        children_query.get_mut(swap.entity.clone()).unwrap().swap(swap.index1, swap.index2);
            
        // children.swap(swap.index1, swap.index2);
        // commands.entity(swap.entity).replace_children(children.as_mut_slice());
    }

}

fn debug_array(
    keyboard_input: Res<ButtonInput<KeyCode>>,
    array: Single<Entity, With<Array>>,
    mut ev_inserts: EventWriter<InsertToArrayEvent>,
    mut ev_removals: EventWriter<RemoveFromArrayEvent>,
    mut ev_swaps: EventWriter<SwapInArrayEvent>,
) {
    let array = array.into_inner();
    if keyboard_input.just_pressed(KeyCode::Digit0) {
        ev_inserts.send(InsertToArrayEvent { entity: array, value: "0".to_string(), index: 0});
    }
    if keyboard_input.just_pressed(KeyCode::Digit7) {
        ev_inserts.send(InsertToArrayEvent { entity: array, value: "7".to_string(), index: 0});
    }
    if keyboard_input.just_pressed(KeyCode::KeyR) {
        ev_removals.send(RemoveFromArrayEvent { entity: array, index: 4});
    }

    if keyboard_input.just_pressed(KeyCode::KeyS) {
        ev_swaps.send(SwapInArrayEvent { entity: array, index1: 0, index2: 4});
    }
}



type InterpolationFn = fn(Vec3, Vec3, f32) -> Vec3;
enum Path {
    LinearInterpolation
}

#[derive(Component)]
struct TargetTransform {
    transform: Transform,
    path: Path,
    total_time: f32,
    time_passed: f32,
}

impl TargetTransform {
    fn new(transform: &Transform, path: Path) -> Self {
        Self {
            transform: transform.clone(),
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




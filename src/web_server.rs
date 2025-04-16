use std::sync::mpsc;
use crate::action::*;
use crate::array::Array;
use bevy::prelude::*;
use std::thread;
use std::time::Duration;



pub fn run(
    data_receiver: mpsc::Receiver<Entity>,
    request_sender: mpsc::Sender<Action>,
) {

    request_sender.send(Action::Create(Structure::Array));

    let entity = data_receiver.recv().expect("Entity will be returned :)");

    request_sender.send(Action::Insert(entity, "h".to_string(), 0));
    
}
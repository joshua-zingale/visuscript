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

    let entity = data_receiver.recv().unwrap();

    request_sender.send(Action::InsertToArray{entity, value: "h".to_string(), index: 0});
    
}
use std::sync::mpsc;
use crate::action::*;
use bevy::prelude::*;
use std::thread;
use std::time::Duration;


pub fn run(
    data_receiver: mpsc::Receiver<(u64, Data)>,
    request_sender: mpsc::Sender<Action>,
) {


    let make_request = |action| {
        request_sender.send(action).expect("The action should have no problem being sent across threads.");
        let (wait_time, data) = data_receiver.recv().expect("Bevy must respond with some data");
        std::thread::sleep(std::time::Duration::from_millis(wait_time));
        data
    };

    let Data::Entity(entity) = make_request(Action::Create(Structure::Array)) else {
        panic!("Did not get entity")
    };

    make_request(Action::InsertToArray{entity, value: "0".to_string(), index: 0});
    make_request(Action::InsertToArray{entity, value: "1".to_string(), index: 0});
    make_request(Action::InsertToArray{entity, value: "2".to_string(), index: 0});
    
}


pub enum Data {
    None,
    Entity(Entity),
    Vector(Vec<String>),
}
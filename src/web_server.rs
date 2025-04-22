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

    let Data::Entity(entity) = make_request(Action::CreateArray(vec!["5".to_string(),"3".to_string(),"0".to_string()])) else {
        panic!("Did not get entity")
    };

    make_request(Action::InsertToArray{entity, value: "9".to_string(), index: 0});
    make_request(Action::InsertToArray{entity, value: "1".to_string(), index: 1});
    // make_request(Action::SetInArray { entity: entity, index: 1, value: "3".to_string() });
    make_request(Action::InsertToArray{entity, value: "5".to_string(), index: 2});
    make_request(Action::InsertToArray{entity, value: "4".to_string(), index: 1});
    make_request(Action::SwapInArray { entity, a_index: 0, b_index: 2 });

}
#[derive(Debug)]
pub enum Data {
    None,
    Entity(Entity),
    Vector(Vec<String>),
}
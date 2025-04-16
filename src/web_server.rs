use std::sync::mpsc;
use crate::action::*;
use bevy::prelude::Entity;


pub fn run(
    request_sender: mpsc::Sender<Action>,
) {
    // request_sender.send(Action::Insertion(, "h", 0));
}
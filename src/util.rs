use bevy::prelude::*;

#[derive(Component)]
pub struct DespawnTimer {
    time: f32
}

impl DespawnTimer {
    pub fn new(time: f32) -> DespawnTimer {
        DespawnTimer { time }
    }
    pub fn tick(&mut self, delta: f32) {
        self.time =  match self.time {
            ..=0.0 => 0.0,
            t => t - delta,
        };
    }
    pub fn done(&self) -> bool{
        self.time <= 0.0
    }
}


#[derive(Component)]
#[require(Transform)]
pub struct DespawnOnTouch {
    pub entity: Entity,
    pub radius: f32
}

impl DespawnOnTouch {
    pub fn new(entity: Entity, radius: f32) -> DespawnOnTouch {
        DespawnOnTouch { entity, radius }
    }
}
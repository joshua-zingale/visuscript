use super::entity::Entity;


#[derive(Debug)]
struct EntityNotFound;

#[derive(Default)]
pub struct Arena<T> 
where T: Default {
    data: Vec<T>,
    sparse_map: Vec<Option<usize>>,
    dense_map: Vec<Entity>,
}

impl<T> Arena<T>
where T: Default
{
    pub fn mut_borrow_for(&mut self, entity: Entity) -> Option<&mut T> {
        match self.sparse_map[entity.0] {
            None => None,
            Some(arena_index) => Some(&mut self.data[arena_index])
        }
    }
    pub fn borrow_for(&self, entity: Entity) -> Option<&T> {
        match self.sparse_map[entity.0] {
            None => None,
            Some(arena_index) => Some(&self.data[arena_index])
        }
    }
    pub fn add_for(&mut self, entity: Entity) {
        let index = self.data.len();
        self.data.push(T::default());
        self.sparse_map[entity.0] = Some(index);
        self.dense_map[index] = entity;
    }

    pub fn remove_for(&mut self, entity: Entity) -> Result<(), EntityNotFound> {
        match self.sparse_map[entity.0] {
            None => Err(EntityNotFound)?,
            Some(arena_index) => {
                let last_data_index = self.data.len() - 1;
                self.data.swap(arena_index, last_data_index);

                let last_dense_map_index = self.dense_map.len() - 1;
                self.dense_map.swap(arena_index, last_dense_map_index);

                self.data.pop();
                self.dense_map.pop();
                self.sparse_map[entity.0] = None;
            }
        }
        Ok(())
    }
}
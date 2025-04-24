use std::net::{TcpListener, TcpStream};
use std::sync::mpsc;
use std::io::{prelude::*, BufReader};

use crate::action::*;
use bevy::prelude::*;
use std::io::{Error, ErrorKind};
use serde::{Serialize, Deserialize};
use serde_json;


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


    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        let(status_line, contents) = match process_request(&stream) {
            Err(e) => {
                ("HTTP/1.1 400 Bad Request".to_string(), e.to_string())
            }
            Ok(action) => {
                (
                    "HTTP/1.1 200 OK".to_string(),
                    serde_json::to_string(&make_request(action)).expect("The data from Bevy must serialize.")
                )
            }
        };


        make_response(stream, status_line, contents);



    }
   
}



fn process_request(stream: &TcpStream) -> Result<Action, Error> {
    let mut buf_reader = BufReader::new(stream);
    let mut headers = std::collections::HashMap::new();
    let mut request_line = String::new();


    buf_reader.read_line(&mut request_line).map_err(|_| Error::new(ErrorKind::Other, "Error reading request line"))?;

    if request_line.is_empty() {
        return Err(Error::new(ErrorKind::Other, "Empty request line."));
    }

    loop {
        let mut header_line = String::new();
        buf_reader.read_line(&mut header_line).map_err(|_| Error::new(ErrorKind::Other, "Error reading request line"))?;
        if header_line.trim().is_empty() {
            break; // End of headers
        }

        if let Some((key, value)) = header_line.split_once(":") {
            headers.insert(key.trim().to_lowercase(), value.trim().to_string());
        }
    }


    let Some(content_length_str) = headers.get("content-length") else {
        return Err(Error::new(ErrorKind::Other, "Did not get content-length in HTTP request."));
    };

    let Ok(content_length) = content_length_str.parse::<usize>() else {
        return Err(Error::new(ErrorKind::Other, "Did not get valid content-length in HTTP"));
    };

    let mut buffer = vec![0; content_length];
    let Ok(bytes_read) = buf_reader.read(&mut buffer) else {
        return Err(Error::new(ErrorKind::Other, "Could not read content of HTTP request."));
    };

    if bytes_read != content_length {
        return Err(Error::new(ErrorKind::Other, format!("Received the wrong number of bytes in the HTTP request's content: {bytes_read} instead of {content_length}.")));
    }

    let content = String::from_utf8_lossy(&buffer).to_string();
    
    
    let action = match Action::from_json(&content) {
        Ok(action) => action,
        Err(e) => return Err(Error::new(ErrorKind::Other, format!("Received invalid JSON: {e}")))
    };


    Ok(action)
}


fn make_response(mut stream: TcpStream, status_line: String, contents: String) {
    let length = contents.bytes().len();
    let response = format!("{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}");
    stream.write_all(response.as_bytes()).unwrap();
}

#[derive(Serialize, Deserialize, Debug)]
pub enum Data {
    None,
    Value(String),
    Entity(Entity),
    Vector(Vec<String>),
}
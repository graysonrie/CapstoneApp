use std::net::SocketAddr;
use tokio::{net::TcpListener, sync::oneshot, task::JoinHandle};

use crate::prelude::*;

#[allow(dead_code)]
pub struct TestServer {
    pub addr: String,
    shutdown: Option<oneshot::Sender<()>>,
    handle: JoinHandle<()>,
    pub config: AppConfig,
}

impl TestServer {
    #[allow(dead_code)]
    pub async fn spawn(app: Router, config: AppConfig) -> Self {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();

        let (tx, rx) = oneshot::channel::<()>();

        let handle = tokio::spawn(async move {
            axum::serve(
                listener,
                app.into_make_service_with_connect_info::<SocketAddr>(),
            )
            .with_graceful_shutdown(async {
                let _ = rx.await;
            })
            .await
            .unwrap();
        });

        Self {
            addr: format!("http://{addr}"),
            shutdown: Some(tx),
            handle,
            config,
        }
    }

    #[allow(dead_code)]
    pub fn signal_shutdown(&mut self) {
        if let Some(tx) = self.shutdown.take() {
            let _ = tx.send(());
        }
    }

    #[allow(dead_code)]
    pub async fn shutdown(mut self) {
        self.signal_shutdown();
        let _ = self.handle.await;
    }
}

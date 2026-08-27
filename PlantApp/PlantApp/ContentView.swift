//
//  ContentView.swift
//  PlantApp
//
//  Created by Grayson Rieger on 8/25/26.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            NavigationStack {
                HomeView()
            }.tabItem {
                Label("Home", systemImage: "house.fill")
            }
            
            NavigationStack {
                PlantCameraView()
            }.tabItem {
                Label("Camera", systemImage: "camera.fill")
            }

            NavigationStack {
                LoginView()
            }.tabItem {
                Label("Profile", systemImage: "person.crop.circle.fill")
            }
        }
    }
}

#Preview {
    ContentView()
}

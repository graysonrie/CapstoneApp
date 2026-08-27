import SwiftUI

struct LoginView: View {
    
    var body: some View {
        
        ZStack {
//            Image("LoginBackground")
//                .resizable()
//                .scaledToFill()
//                .frame(minWidth: 0, maxWidth: .infinity, minHeight: 0, maxHeight: .infinity)
//                .clipped()
//                .overlay {
//                    Brand.green.opacity(0.35)
//                }
//                .ignoresSafeArea()
//            
            
            VStack(spacing: 24) {  // Actual view
                Spacer(minLength: 0)
                
                Text("Plant app")
                    .font(Brand.font(40, weight: .bold))
                    .foregroundStyle(.background)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .lineSpacing(CGFloat(0))
                    .padding(32)
                LoginFormView { fullName, email, password in
                    
                }
                
                Spacer().frame(height: 48)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        
    }
}

#Preview {
    NavigationStack {
        LoginView()
    }
}

import SwiftUI

struct LoginFormView: View {
    let onLogin: (_ fullName: String, _ email: String, _ password: String) async -> Void
    
    @State private var fullName = ""
    @State private var email = ""
    @State private var password = ""
    
    var body: some View {
        
        
        VStack(spacing: 24) {  // Login Form box
            
            

            VStack(spacing: 20) {
                UnderlinedField(title: "Full Name") {
                    TextField("", text: $email)
                        .textContentType(.emailAddress)
                        .keyboardType(.emailAddress)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }
                
                UnderlinedField(title: "Email") {
                    TextField("", text: $email)
                        .textContentType(.emailAddress)
                        .keyboardType(.emailAddress)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }

                UnderlinedField(title: "Password") {
                    SecureField("", text: $password)
                        .textContentType(.password)
                }
            }
            
            Button {
                // Login action
            } label: {
                Text("Log In")
                    .font(Brand.font(18, weight:.bold))
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Brand.green)
                    .foregroundStyle(.white)
            }
            .disabled(email.isEmpty || password.isEmpty)
            
            VStack {
                Text("Don't have an account?")
                    .font(Brand.font(16))
                    .foregroundStyle(.secondary)
                
                Text("Create one")
                    .font(Brand.font(16, weight: .bold))
                    .foregroundStyle(Brand.green)
            }
        }
        .padding(24)
        
    }
}

private struct UnderlinedField<Field: View>: View {
    let title: String
    @ViewBuilder let field: () -> Field

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title.uppercased())
                .font(Brand.font(12, weight: .bold))
                .foregroundStyle(.secondary)
                .tracking(0.6)

            field()
                .font(Brand.font(17))
                .foregroundStyle(.primary)
                .textFieldStyle(.plain)
                .padding(.vertical, 4)

            Rectangle()
                .fill(Color.secondary.opacity(0.45))
                .frame(height: 1)
        }
    }
}

#Preview {
    LoginFormView { _, _ , _ in }
}

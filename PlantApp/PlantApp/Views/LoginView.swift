import SwiftUI

struct LoginView: View {
    @State private var email = ""
    @State private var password = ""

    var body: some View {

        ZStack {
            Image("LoginBackground")
                .resizable()
                .scaledToFill()
                .frame(minWidth: 0, maxWidth: .infinity, minHeight: 0, maxHeight: .infinity)
                .clipped()
                .overlay {
                    Color.brandGreen.opacity(0.35)
                }
                .ignoresSafeArea()

            VStack(spacing: 24) {  // Actual view
                Spacer(minLength: 0)

                Text("Plant app")
                    .font(.custom("NotoSansOriya-Bold", size: 40))
                    .foregroundStyle(.background)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .lineSpacing(CGFloat(0))
                    .padding(32)

                VStack(spacing: 24) {  // Login Form box

                    VStack {
                        Text("Sign in to scan your plants")
                            .font(.custom("NotoSansOriya", size: 16))
                            .foregroundStyle(.brandGreen)
                    }

                    VStack(spacing: 16) {
                        HStack(spacing: 12) {
                            Image(systemName: "envelope")
                                .foregroundStyle(.secondary)
                            TextField("Email", text: $email)
                                .textContentType(.emailAddress)
                                .keyboardType(.emailAddress)
                                .textInputAutocapitalization(.never)
                                .autocorrectionDisabled()
                        }
                        .padding()
                        .background(.background, in: RoundedRectangle(cornerRadius: 10))
                        .shadow(color: .black.opacity(0.10), radius: 6, x: 0, y: 2)

                        HStack(spacing: 12) {
                            Image(systemName: "lock")
                                .foregroundStyle(.secondary)
                            SecureField("Password", text: $password)
                                .textContentType(.password)
                        }
                        .padding()
                        .background(.background, in: RoundedRectangle(cornerRadius: 10))
                        .shadow(color: .black.opacity(0.10), radius: 6, x: 0, y: 2)
                    }

                    Button {
                        // Login action
                    } label: {
                        Text("Log In")
                            .font(.custom("NotoSansOriya", size: 18))
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(.brandGreen)
                            .foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                    }
                    .disabled(email.isEmpty || password.isEmpty)

                    VStack {
                        Text("Don't have an account?")
                            .font(.custom("NotoSansOriya", size: 16))
                            .foregroundStyle(.brandGreen)

                        Text("Create one")
                            .font(.custom("NotoSansOriya-Bold", size: 16))
                            .foregroundStyle(.brandGreen)
                    }
                }
                .padding(24)
                .background {
                    RoundedRectangle(cornerRadius: 16)
                        .fill(.background)
                        .shadow(color: .black.opacity(0.12), radius: 8, y: 4)
                }
                .padding(.horizontal)

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

import SwiftUI

enum Brand {
    /// Matches `BrandGreen` in Assets.xcassets.
    /// Prefer this over `Color.brandGreen` when the IDE can't see Xcode's generated asset symbols.
    static let green = Color("BrandGreen")

    private static let regularFontName = "NotoSansOriya"
    private static let boldFontName = "NotoSansOriya-Bold"

    static func font(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        let name = Self.fontName(for: weight)
        return .custom(name, size: size)
    }

    private static func fontName(for weight: Font.Weight) -> String {
        switch weight {
        case .bold, .semibold, .heavy, .black:
            return boldFontName
        default:
            return regularFontName
        }
    }
}

use async_openai::{
    Client,
    config::OpenAIConfig,
    types::{
        ChatCompletionRequestMessage,
        ChatCompletionRequestMessageContentPartText,
        ChatCompletionRequestSystemMessageArgs,
        ChatCompletionRequestUserMessageArgs,
        ChatCompletionRequestUserMessageContent,
        ChatCompletionRequestUserMessageContentPart,
        CreateChatCompletionRequestArgs,
        ImageDetail,
        ImageUrl,
        ResponseFormat,
    },
};
use base64::Engine;

use super::errors::PlantScanError;
use crate::prelude::*;

const SYSTEM_PROMPT: &str = r#"You are a plant identification assistant for a consumer iOS application.

Your job is to analyze the supplied image and identify the primary plant visible in it.

Priorities:
1. Identify the plant as accurately as possible.
2. Do not claim certainty when the image is ambiguous.
3. Prefer the most specific identification supported by visible evidence.
4. If species-level identification is uncertain, provide the most likely genus or broader classification instead.
5. Do not invent visual characteristics that are not visible in the image.
6. Provide concise, useful information for a general audience.
7. Clearly distinguish common knowledge from plant-care recommendations that may vary by climate or cultivar.

When identifying the plant, consider:
- leaf shape
- leaf arrangement
- venation
- leaf margins
- flowers
- fruit
- stems
- bark
- growth habit
- visible environmental context

If multiple plants are visible, identify the plant that is most prominent in the image.

If the image does not contain enough information to reasonably identify a plant, indicate that identification is uncertain and explain what additional photo would help, such as:
- a close-up of the leaves
- flowers
- fruit
- stem or bark
- the entire plant

Set is_plant to false when the image does not contain a plant (for example a person, animal, object, landscape with no plant, or an unreadable photo). When is_plant is false, leave identification names null, use Low confidence, empty summary/sections as needed, and explain why in identification_notes.

Return only a JSON object matching this schema:
{
  "is_plant": boolean,
  "identification": {
    "common_name": string | null,
    "scientific_name": string | null,
    "family": string | null,
    "confidence": "High" | "Medium" | "Low",
    "rarity": "Common" | "Uncommon" | "Rare" | "SuperRare" | "Exotic" | null
  },
  "summary": string,
  "sections": {
    "appearance": string,
    "native_range": string | null,
    "care": {
      "light": string | null,
      "watering": string | null,
      "soil": string | null,
      "temperature": string | null
    } | null,
    "interesting_facts": string[],
    "toxicity": {
      "humans": string | null,
      "pets": string | null
    } | null
  },
  "identification_notes": {
    "reasoning_summary": string | null,
    "uncertainty": string | null
  }
}
"#;

pub async fn identify_plant(
    api_key: &str,
    model: &str,
    image_bytes: &[u8],
    mime: &str,
) -> Result<PlantScan, PlantScanError> {
    let encoded = base64::engine::general_purpose::STANDARD.encode(image_bytes);
    let data_url = format!("data:{mime};base64,{encoded}");

    let config = OpenAIConfig::new().with_api_key(api_key);
    let client = Client::with_config(config);

    let request = CreateChatCompletionRequestArgs::default()
        .model(model)
        .response_format(ResponseFormat::JsonObject)
        .messages(vec![
            ChatCompletionRequestMessage::System(
                ChatCompletionRequestSystemMessageArgs::default()
                    .content(SYSTEM_PROMPT)
                    .build()
                    .map_err(|err| PlantScanError::OpenAi(err.to_string()))?,
            ),
            ChatCompletionRequestMessage::User(
                ChatCompletionRequestUserMessageArgs::default()
                    .content(ChatCompletionRequestUserMessageContent::Array(vec![
                        ChatCompletionRequestUserMessageContentPart::Text(
                            ChatCompletionRequestMessageContentPartText {
                                text: "Identify the primary plant in this image and provide information about it."
                                    .to_string(),
                            },
                        ),
                        ChatCompletionRequestUserMessageContentPart::ImageUrl(
                            async_openai::types::ChatCompletionRequestMessageContentPartImage {
                                image_url: ImageUrl {
                                    url: data_url,
                                    detail: Some(ImageDetail::Auto),
                                },
                            },
                        ),
                    ]))
                    .build()
                    .map_err(|err| PlantScanError::OpenAi(err.to_string()))?,
            ),
        ])
        .build()
        .map_err(|err| PlantScanError::OpenAi(err.to_string()))?;

    let response = client
        .chat()
        .create(request)
        .await
        .map_err(|err| PlantScanError::OpenAi(err.to_string()))?;

    let content = response
        .choices
        .first()
        .and_then(|choice| choice.message.content.as_ref())
        .ok_or(PlantScanError::InvalidModelResponse)?;

    serde_json::from_str(content).map_err(|err| {
        tracing::error!("failed to parse plant scan JSON: {err}; body={content}");
        PlantScanError::InvalidModelResponse
    })
}

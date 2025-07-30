package com.example.geminilivedemo

import org.json.JSONObject

class Response(data: JSONObject) {
    var text: String? = null
    var audioData: String? = null

    init {
        if (data.has("text")) {
            text = data.getString("text")
        }

        if (data.has("audio")) {
            audioData = data.getString("audio")
        }
    }
}

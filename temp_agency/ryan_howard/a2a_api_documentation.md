# Ryan Howard A2A Server API Documentation

This document explains how to interact with the Ryan Howard A2A server, which provides data analysis capabilities. The API supports both streaming and non-streaming modes.

## API Base URL

```
http://localhost:10010/
```

## Authentication

All API requests require Basic Authentication:

```
Authorization: Basic $(echo -n 'admin:password' | base64)
```

## API Endpoints

The A2A server exposes JSON-RPC 2.0 endpoints for message processing.

### 1. Streaming Messages (`message/stream`)

The streaming endpoint allows you to send messages and receive responses in real-time as they're being generated.

#### Request Format

```bash
curl -N -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
  -d '{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "message/stream",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Your message here"
        }
      ],
      "messageId": "msg-01",
      "metadata": {
        "user_id": "username"
      }
    }
  }
}'
```

#### Response Format

The streaming response comes in chunks, with each chunk prefixed by `data: `. Each chunk contains a JSON object with information about the ongoing task:

1. Initially, you receive the task status as "submitted"
2. As processing continues, you'll receive "working" status updates
3. You'll receive intermediate content via "artifact-update" events
4. Finally, you'll receive a "completed" status update

#### Session Management with `contextId`

- **First Request**: The first request doesn't include a `contextId`. The server generates a new one and returns it in the response.
- **Subsequent Requests**: You can include the `contextId` from previous responses to continue the same conversation:

```bash
curl -N -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
  -d '{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "message/stream",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Your follow-up message"
        }
      ],
      "messageId": "msg-02",
      "contextId": "046e0788-8519-4986-b967-a62c4dc1d5ba",
      "metadata": {
        "user_id": "username"
      }
    }
  }
}'
```

You can either:
- Use the `contextId` from a previous response to continue a conversation
- Omit the `contextId` to start a new conversation
- Provide your own `contextId` to start a new conversation with a specific identifier

### 2. Non-Streaming Messages (`message/send`)

For simpler use cases, you can use the non-streaming endpoint to send a message and receive the complete response at once.

#### Request Format

```bash
curl -N -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
  -d '{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Your complete message with all details"
        }
      ],
      "messageId": "msg-01"
    }
  }
}'
```

#### Response Format

The non-streaming response is a single JSON object containing:
- The complete message history
- The final result
- Any artifacts generated (like charts or other outputs)
- The task status (typically "completed")

## Examples

### Example 1: Data Analysis with Streaming (Initial Request)

```bash
curl -N -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
  -d '{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "message/stream",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Hey, can you load the datafile and provide me some insights about the data? also can you create a pie chart for the Race and Gender columns?"
        }
      ],
      "messageId": "msg-01",
      "metadata": {
        "user_id": "venkateshwaranr"
      }
    }
  }
}'
```

### Example 2: Follow-up Request (Using contextId)

```bash
curl -N -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
  -d '{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "message/stream",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Ahh sorry man, here you go: /app/ryan_howard/test_data/heroes_information.csv"
        }
      ],
      "messageId": "msg-02",
      "contextId": "046e0788-8519-4986-b967-a62c4dc1d5ba",
      "metadata": {
        "user_id": "venkateshwaranr"
      }
    }
  }
}'
```

### Example 3: Non-Streaming Request (Complete Information)

```bash
curl -N -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
  -d '{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Hey, can you load the datafile /app/ryan_howard/test_data/heroes_information.csv and provide me some insights about the data? also can you create a pie chart for the Race and Gender columns?"
        }
      ],
      "messageId": "msg-01"
    }
  }
}'
```

## Key Differences Between Streaming and Non-Streaming

1. **Method Name**:
   - Streaming: `message/stream`
   - Non-streaming: `message/send`

2. **Response Behavior**:
   - Streaming: Provides real-time updates with multiple JSON chunks
   - Non-streaming: Returns a single, complete response when processing is finished

3. **Use Cases**:
   - Streaming: Better for long-running operations where you want to show progress
   - Non-streaming: Simpler integration when you can wait for the complete response

4. **Session Management**:
   - Both methods support the `contextId` for continuing conversations
   - Omitting the `contextId` starts a new conversation

Attribute VB_Name = "Module1"
Sub QueryGpt()
    Dim sld As Slide
    Dim shp As Shape
    Dim text As String
    Dim explanation As String
    Dim prompt As String
    Dim subject As String
    
    ' Extract and format the text from the current slide
    Set sld = ActiveWindow.View.Slide
    For Each shp In sld.Shapes
        If shp.HasTextFrame Then
            If shp.TextFrame.HasText Then
                text = text & " [" & Replace(shp.TextFrame.TextRange.text, vbCrLf, "/") & "] "
            End If
        End If
    Next shp
    text = Replace(Replace(Replace(text, vbCrLf, "\n"), vbCr, "\r"), vbLf, "\n")
    
    subject = "The concept of Public Domain"
    prompt = "You are a useful assistant that explains the concepts from a presentation about " & subject & ". Explain the following concepts: "
    explanation = CallOpenAI(prompt & text)
    
    ' Append the AI explanation to the slide notes
    sld.NotesPage.Shapes.Placeholders(2).TextFrame.TextRange.InsertAfter vbCrLf & explanation
End Sub

Function CallOpenAI(text As String) As String
    Dim httpRequest As Object
    Dim responseText As String
    Dim contentStartPos As Long
    Dim contentEndPos As Long

    ' Prepare the connection and send the request to the OpenAI API
    Set httpRequest = CreateObject("WinHttp.WinHttpRequest.5.1")
    httpRequest.Open "POST", "https://protect-eu.mimecast.com/s/Wv-oCzBE4IMx029t4gzLo?domain=api.openai.com", False
    httpRequest.setTimeouts 0, 60000, 30000, 120000
    httpRequest.setRequestHeader "Content-Type", "application/json"
    httpRequest.setRequestHeader "Authorization", "Bearer " & Environ("OPENAI_API_KEY")
    httpRequest.Send "{""model"": ""gpt-3.5-turbo"", " _
                & """messages"": [{""role"": ""user"", " _
                & """content"": """ & text & """}]}"
    httpRequest.WaitForResponse
    responseText = httpRequest.responseText
    
    ' Extract the AI answer from the response string
    contentStartPos = InStr(1, responseText, """content"":""") + 11
    responseText = Mid(responseText, contentStartPos)
    contentEndPos = InStr(1, responseText, """") - 1
    responseText = Replace(Mid(responseText, 1, contentEndPos), "\n", vbCrLf)

    CallOpenAI = responseText
End Function



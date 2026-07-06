# $testCases = @(
#     "I am SC category, studying, family income 1.5 lakh per year",
#     "I am general category, employed, family income 12 lakh per year",
#     "I am OBC category with a disability, currently studying",
#     "I am ST category, senior citizen aged 65, family income 80000 per year",
#     "I am Muslim minority community, studying, low income family",
#     "I am general category, working as a teacher, not a student",
#     "I am a student but not sure about my family income",
#     "What is the weather like today",
#     "What is the capital of France",
#     "I need help"
# )

# $results = @()
# foreach ($tc in $testCases) {
#     $body = @{ description = $tc } | ConvertTo-Json
#     try {
#         $response = Invoke-RestMethod -Uri "https://scheme-navigator-backend.onrender.com/check-eligibility" -Method Post -ContentType "application/json" -Body $body
#         $results += [PSCustomObject]@{
#             Input = $tc
#             OnTopic = if ($response.refusal_message) { "false" } else { "true" }
#             RefusalMessage = $response.refusal_message
#             NumResults = $response.final_results.Count
#             Schemes = ($response.final_results | ForEach-Object { $_.scheme_name }) -join ", "
#         }
#     } catch {
#         $results += [PSCustomObject]@{ Input = $tc; OnTopic = "ERROR"; RefusalMessage = $_.Exception.Message; NumResults = 0; Schemes = "" }
#     }
# }

# $results | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 test_results.json
# $results | Format-Table -Wrap -AutoSize


$testCases = @(
    "I am SC category, studying, family income 1.5 lakh per year",
    "I am general category, employed, family income 12 lakh per year",
    "I am OBC category with a disability, currently studying",
    "I am ST category, senior citizen aged 65, family income 80000 per year",
    "I am Muslim minority community, studying, low income family",
    "I am general category, working as a teacher, not a student",
    "I am a student but not sure about my family income",
    "What is the weather like today",
    "What is the capital of France",
    "I need help"
)

$results = @()
foreach ($tc in $testCases) {
    $body = @{ description = $tc } | ConvertTo-Json
    try {
        $response = Invoke-RestMethod -Uri "https://scheme-navigator-backend.onrender.com/check-eligibility" -Method Post -ContentType "application/json" -Body $body
        $results += [PSCustomObject]@{
            Input = $tc
            OnTopic = if ($response.refusal_message) { "false" } else { "true" }
            RefusalMessage = $response.refusal_message
            NumResults = $response.final_results.Count
            Schemes = ($response.final_results | ForEach-Object { $_.scheme_name }) -join ", "
        }
    } catch {
        $results += [PSCustomObject]@{ Input = $tc; OnTopic = "ERROR"; RefusalMessage = $_.Exception.Message; NumResults = 0; Schemes = "" }
    }
    Start-Sleep -Seconds 3
}

$results | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 test_results.json
Write-Host "Done. Results saved to test_results.json"
# Kigali HomeTech RAG Chatbot — Test Questions

Use these questions after the backend and frontend are running. For every answer, check that:

- The answer is clear and supported by the approved documents.
- Source badges appear below the answer.
- The Transparency panel shows the real query, retrieval, prompt, and verification steps.
- The chatbot says it does not know when the documents do not contain the answer.

## 1. Returns

1. Can I return a blender after 14 days?
2. How many days do I have to return a product?
3. What proof do I need when returning an item?
4. Can I return a product without its accessories?
5. Can I exchange a damaged product?
6. How will I receive my refund?

Expected test: The chatbot should mainly retrieve pages from `Return_Policy.pdf` and show their page numbers below the answer.

## 2. Warranty

1. How long is the warranty period?
2. What does the warranty cover?
3. What is not covered by the warranty?
4. How do I submit a warranty claim?
5. Which documents are required for a warranty claim?
6. Does the warranty cover accidental damage?

Expected test: The chatbot should mainly retrieve pages from `Warranty_Policy.pdf`.

## 3. Delivery

1. How long does delivery take within Kigali?
2. Does Kigali HomeTech deliver outside Kigali?
3. How can I track my delivery?
4. What should I do if my product arrives damaged?
5. Can another person receive my order?
6. Can I change my delivery address?

Expected test: The chatbot should mainly retrieve pages from `Delivery_Guide.pdf`.

## 4. Payments and common questions

1. Which payment methods are accepted?
2. Can I pay using Mobile Money?
3. Can I pay when the product is delivered?
4. Do you accept bank transfers?
5. What time does the store open?
6. How can I contact customer support?

Expected test: The chatbot should mainly retrieve information from `FAQ.txt`.

## 5. Product instructions

1. How should I clean the SmartBlend 500?
2. What should I do before using the blender?
3. What should I do if the blender stops working?
4. How should I install the CoolHome 200 refrigerator?
5. How long should the refrigerator stand before being switched on?
6. How can I clean the refrigerator safely?

Expected test: The chatbot should retrieve the relevant product manual instead of a policy document.

## 6. Missing-information safety test

1. Does the store sell laptops?
2. Can I get a 50% student discount?
3. Does Kigali HomeTech provide international delivery?
4. Can the store repair my car?
5. Who is the current manager of Kigali HomeTech?

Expected test: If the approved documents do not contain the requested information, the chatbot should say: **“I do not know from the available business documents.”** It should not invent an answer.

## Test results

| Number | Question | Correct answer? | Correct sources? | Transparency works? | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 |  | Yes / No | Yes / No | Yes / No |  |
| 2 |  | Yes / No | Yes / No | Yes / No |  |
| 3 |  | Yes / No | Yes / No | Yes / No |  |
| 4 |  | Yes / No | Yes / No | Yes / No |  |
| 5 |  | Yes / No | Yes / No | Yes / No |  |

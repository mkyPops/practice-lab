/**
 * Postman "Tests" script.
 *
 * Validates that the response body conforms to a predefined JSON Schema
 * before making any assertions against individual fields. This guards
 * against silently asserting on a malformed/unexpected payload shape.
 */

// JSON Schema describing the expected shape of the response body
const userSchema = {
    type: "object",
    required: ["id", "email", "name", "isActive", "roles"],
    properties: {
        id: { type: "integer", minimum: 1 },
        email: { type: "string", format: "email" },
        name: { type: "string", minLength: 1 },
        isActive: { type: "boolean" },
        roles: {
            type: "array",
            items: { type: "string" },
            minItems: 1
        },
        createdAt: { type: "string", format: "date-time" }
    },
    additionalProperties: true
};

let responseBody;

pm.test("Response body is valid JSON", function () {
    // Throws (and fails the test) if the body cannot be parsed
    responseBody = pm.response.json();
});

pm.test("Response matches the user JSON schema", function () {
    pm.expect(responseBody).to.be.jsonSchema(userSchema);
});

// Only assert on individual fields once the schema check above has passed,
// otherwise a malformed payload could produce confusing downstream failures.
if (responseBody) {
    pm.test("Status code is 200", function () {
        pm.response.to.have.status(200);
    });

    pm.test("User id is a positive integer", function () {
        pm.expect(responseBody.id).to.be.a("number");
        pm.expect(responseBody.id).to.be.above(0);
    });

    pm.test("Email field looks valid", function () {
        pm.expect(responseBody.email).to.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
    });

    pm.test("User is active", function () {
        pm.expect(responseBody.isActive).to.eql(true);
    });

    pm.test("Roles array contains at least one role", function () {
        pm.expect(responseBody.roles).to.be.an("array").that.is.not.empty;
    });
}

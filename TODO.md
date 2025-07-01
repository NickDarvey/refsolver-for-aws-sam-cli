# TODO

## [ ] Make AWS SAM CLI-friendly

So far we've got neat library functions which can be composed together. However, our users just want to use SAM CLI.

That is, we want them to be able to call `sam local invoke MyFunction --env-vars MyFunction.env.json --profile sandbox` using an `.env.json` we have generated for them where we've resolved any refs.

We should not wrap calls (to SAM CLI or CDK CLI) but keep writing things in a composable manner.

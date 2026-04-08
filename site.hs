{-# LANGUAGE OverloadedStrings #-}

import Hakyll

main :: IO ()
main = hakyll $ do
  match "css/*" $ do
    route   idRoute
    compile copyFileCompiler

  match "logo/*" $ do
    route   idRoute
    compile copyFileCompiler

  match "favicon.svg" $ do
    route   idRoute
    compile copyFileCompiler

  match "content/index.md" $ do
    route   $ setExtension "html" `composeRoutes` gsubRoute "content/" (const "")
    compile $ mathPandocCompiler
          >>= loadAndApplyTemplate "templates/home.html"    postCtx
          >>= loadAndApplyTemplate "templates/default.html" postCtx
          >>= relativizeUrls

  match "content/**.md" $ do
    route   $ setExtension "html" `composeRoutes` gsubRoute "content/" (const "")
    compile $ mathPandocCompiler
          >>= loadAndApplyTemplate "templates/page.html"    postCtx
          >>= loadAndApplyTemplate "templates/default.html" postCtx
          >>= relativizeUrls

  match "templates/*" $ compile templateBodyCompiler

postCtx :: Context String
postCtx = defaultContext

mathPandocCompiler :: Compiler (Item String)
mathPandocCompiler = pandocCompilerWith defaultHakyllReaderOptions defaultHakyllWriterOptions
